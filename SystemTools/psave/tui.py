#!/usr/bin/env python3
"""Responsive psave task manager. Python standard library only."""
import collections
import curses
import locale
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

locale.setlocale(locale.LC_ALL, '')
HOME = Path.home()
HELPER = os.environ.get('PSAVE_HELPER_PATH', str(HOME / '.local/bin/psave'))
BAT = Path('/sys/class/power_supply/macsmc-battery')
SCREEN = Path('/sys/class/backlight/apple-panel-bl')
ACTIONS = [
    ('School mode', ['school']), ('Restore settings', ['restore']),
    ('Power saver only', ['on']), ('Balanced profile', ['balanced']),
    ('Dim screen 10%', 'dim-down'), ('Brighten screen 10%', 'dim-up'),
    ('Bluetooth off', ['bluetooth', 'off']), ('Bluetooth on', ['bluetooth', 'on']),
    ('Open btop', ['btop']), ('Install PowerTOP (sudo)', ['install-tools']),
    ('Trim system logs/cache (sudo)', ['clean-system']), ('Suspend now', ['suspend']),
]


def read(path, default=''):
    try:
        return Path(path).read_text().strip()
    except (OSError, ValueError):
        return default


def number(path, default=None):
    try:
        return float(read(path))
    except ValueError:
        return default


def percent(value, total):
    return 100 * value / total if total else 0


def size(value):
    for unit in ('B', 'K', 'M', 'G', 'T'):
        if abs(value) < 1024:
            return f'{value:.0f}{unit}' if unit == 'B' else f'{value:.1f}{unit}'
        value /= 1024
    return f'{value:.1f}P'


def brightness():
    return round(percent(number(SCREEN / 'brightness', 0), number(SCREEN / 'max_brightness', 1)))


def proc_info(pid):
    """Parse after the final ')' so spaces/parentheses in comm are safe."""
    raw = read(f'/proc/{pid}/stat')
    end = raw.rfind(')')
    fields = raw[end + 2:].split()
    if end < 0 or len(fields) < 22:
        return None
    try:
        return {'pid': int(pid), 'name': raw[raw.find('(') + 1:end],
                'ticks': int(fields[11]) + int(fields[12]), 'start': int(fields[19]),
                'rss': max(0, int(fields[21])) * os.sysconf('SC_PAGE_SIZE'),
                'uid': Path(f'/proc/{pid}').stat().st_uid, 'state': fields[0]}
    except (ValueError, OSError):
        return None


class Metrics:
    def __init__(self):
        self.history = {k: collections.deque(maxlen=600) for k in ('cpu', 'ram', 'watts', 'battery', 'net', 'io')}
        self.last_cpu = {}
        self.last_process = {}
        self.last_time = None
        self.last_net = None
        self.last_io = None
        self.energy = collections.deque(maxlen=31)
        self.cpu = self.ram = self.mem_used = self.mem_total = 0
        self.rx = self.tx = self.io = 0
        self.watts = self.capacity = None
        self.status = 'unavailable'
        self.profile = 'reading...'
        self.profile_due = 0
        self.cores = []
        self.processes = []
        self.interval = 2
        self.disk = shutil.disk_usage(HOME)

    def sample(self):
        now = time.monotonic()
        elapsed = now - self.last_time if self.last_time is not None else None
        cores = []
        for line in read('/proc/stat').splitlines():
            fields = line.split()
            if not fields or not fields[0].startswith('cpu'):
                continue
            try:
                values = list(map(int, fields[1:9]))
                current = (sum(values), values[3] + values[4])
            except (ValueError, IndexError):
                continue
            old = self.last_cpu.get(fields[0], current)
            total, idle = current[0] - old[0], current[1] - old[1]
            load = max(0, min(100, percent(total - idle, total)))
            self.last_cpu[fields[0]] = current
            if fields[0] == 'cpu':
                self.cpu = load
            else:
                cores.append(load)
        self.cores = cores
        mem = {}
        for line in read('/proc/meminfo').splitlines():
            fields = line.split()
            if len(fields) >= 2:
                mem[fields[0].rstrip(':')] = int(fields[1]) * 1024
        self.mem_total = mem.get('MemTotal', 0)
        self.mem_used = self.mem_total - mem.get('MemAvailable', self.mem_total)
        self.ram = percent(self.mem_used, self.mem_total)
        network = [0, 0]
        for line in read('/proc/net/dev').splitlines():
            if ':' in line:
                interface, counters = line.split(':', 1)
                fields = counters.split()
                if interface.strip() != 'lo' and len(fields) >= 9:
                    network[0] += int(fields[0])
                    network[1] += int(fields[8])
        if elapsed and self.last_net:
            self.rx, self.tx = [max(0, (n - o) / elapsed) for n, o in zip(network, self.last_net)]
        self.last_net = network
        disk_bytes = 0
        for line in read('/proc/diskstats').splitlines():
            fields = line.split()
            if len(fields) >= 10 and (Path('/sys/block') / fields[2]).exists() and fields[2].startswith(('nvme', 'sd', 'mmc')):
                disk_bytes += (int(fields[5]) + int(fields[9])) * 512
        if elapsed and self.last_io is not None:
            self.io = max(0, (disk_bytes - self.last_io) / elapsed)
        self.last_io = disk_bytes
        self.disk = shutil.disk_usage(HOME)
        self.capacity = number(BAT / 'capacity')
        self.status = read(BAT / 'status', 'unavailable')
        power = number(BAT / 'power_now')
        self.watts = power / 1e6 if power and power > 0 else None
        energy = number(BAT / 'energy_now')
        if energy is not None:
            self.energy.append((now, energy, self.status))
            old_time, old_energy, old_status = self.energy[0]
            if self.watts is None and self.status == old_status == 'Discharging' and now - old_time >= 15 and old_energy > energy:
                self.watts = (old_energy - energy) * 3600 / 1e6 / (now - old_time)
        procs, current_process = [], {}
        ticks_per_second = os.sysconf('SC_CLK_TCK')
        for directory in Path('/proc').iterdir():
            if not directory.name.isdecimal():
                continue
            info = proc_info(directory.name)
            if info is None:
                continue
            identity = (info['pid'], info['start'])
            previous_ticks = self.last_process.get(identity, info['ticks'])
            info['cpu'] = max(0, (info['ticks'] - previous_ticks) / ticks_per_second / elapsed * 100) if elapsed else 0
            current_process[identity] = info['ticks']
            procs.append(info)
        self.processes = procs
        self.last_process = current_process
        self.last_time = now
        for key, value in [('cpu', self.cpu), ('ram', self.ram), ('watts', self.watts), ('battery', self.capacity), ('net', self.rx + self.tx), ('io', self.io)]:
            self.history[key].append(value)
        if now >= self.profile_due:
            try:
                result = subprocess.run(['busctl', '--system', 'get-property', 'net.hadess.PowerProfiles', '/net/hadess/PowerProfiles', 'net.hadess.PowerProfiles', 'ActiveProfile'], capture_output=True, text=True, timeout=.8)
                self.profile = result.stdout.strip().removeprefix('s ').strip('"') if result.returncode == 0 else 'unavailable'
            except (OSError, subprocess.TimeoutExpired):
                self.profile = 'unavailable'
            self.profile_due = now + 15


class UI:
    def __init__(self, win):
        self.win = win
        self.metrics = Metrics()
        self.tab = 0
        self.compact_graph = 0
        self.selected = 0
        self.selected_pid = None
        self.action = 0
        self.sort = 'cpu'
        self.query = ''
        self.filtering = False
        self.paused = False
        self.message = 'Ready. ? help | b opens btop'
        self.confirm = None
        self.details = None
        self.help = False
        self.colors = [0] * 6
        if curses.has_colors():
            curses.start_color()
            try:
                curses.use_default_colors()
                bg = -1
            except curses.error:
                bg = curses.COLOR_BLACK
            for index, fg in enumerate([curses.COLOR_CYAN, curses.COLOR_GREEN, curses.COLOR_MAGENTA, curses.COLOR_YELLOW, curses.COLOR_BLUE, curses.COLOR_RED], 1):
                curses.init_pair(index, fg, bg)
                self.colors[index - 1] = curses.color_pair(index)
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        win.keypad(True)
        win.timeout(200)

    def text(self, y, x, text, width=None, attr=0):
        h, w = self.win.getmaxyx()
        if y < 0 or y >= h or x < 0 or x >= w:
            return
        width = min(w - x, width if width is not None else w - x)
        if width <= 0:
            return
        text = ''.join(c if c.isprintable() else ' ' for c in str(text))
        try:
            self.win.addnstr(y, x, text, width, attr)
        except curses.error:
            pass

    def box(self, y, x, h, w, title, color):
        if h < 2 or w < 4:
            return
        self.text(y, x, '╭' + '─' * (w - 2) + '╮', w, color)
        for row in range(y + 1, y + h - 1):
            self.text(row, x, '│', 1, color)
            self.text(row, x + w - 1, '│', 1, color)
        self.text(y + h - 1, x, '╰' + '─' * (w - 2) + '╯', w, color)
        self.text(y, x + 2, f' {title} ', w - 4, color | curses.A_BOLD)

    def graph(self, y, x, h, w, history, ceiling, color):
        """Braille area graph: two horizontal by four vertical samples/cell."""
        if h < 1 or w < 1:
            return
        data = list(history)[-w * 2:]
        data = [None] * (w * 2 - len(data)) + data
        bits = [[0] * w for _ in range(h)]
        dot = ((1, 2, 4, 64), (8, 16, 32, 128))
        for px, value in enumerate(data):
            if value is None:
                continue
            filled = max(1, min(h * 4, round(value / max(ceiling, .001) * h * 4)))
            for level in range(filled):
                py = h * 4 - level - 1
                bits[py // 4][px // 2] |= dot[px % 2][py % 4]
        for row, cells in enumerate(bits):
            self.text(y + row, x, ''.join(chr(0x2800 + bit) if bit else ' ' for bit in cells), w, color)

    def chart(self, y, x, h, w, title, key, label, color, ceiling=100):
        self.box(y, x, h, w, title, color)
        if h < 3:
            return
        if h == 3:
            self.graph(y + 1, x + 1, 1, w - 2, self.metrics.history[key], ceiling, color)
        else:
            self.text(y + 1, x + 2, label, w - 4, curses.A_BOLD)
            self.graph(y + 2, x + 1, h - 3, w - 2, self.metrics.history[key], ceiling, color)

    def visible_processes(self):
        query = self.query.casefold()
        return sorted((p for p in self.metrics.processes if query in p['name'].casefold() or query in str(p['pid'])), key=lambda p: (p[self.sort], p['rss'], -p['pid']), reverse=True)

    def processes(self, y, x, h, w):
        procs = self.visible_processes()
        if self.selected_pid is not None:
            self.selected = next((i for i, p in enumerate(procs) if (p['pid'], p['start']) == self.selected_pid), min(self.selected, max(0, len(procs) - 1)))
        self.selected = min(self.selected, max(0, len(procs) - 1))
        self.selected_pid = (procs[self.selected]['pid'], procs[self.selected]['start']) if procs else None
        self.box(y, x, h, w, f'PROCESSES {len(procs)} ↓{self.sort.upper()}', self.colors[1])
        if h < 3:
            return
        header = h >= 5
        if header:
            self.text(y + 1, x + 1, '    PID   CPU%    RAM  NAME', w - 2, curses.A_DIM)
        rows = max(0, h - 2 - int(header))
        start = max(0, self.selected - rows + 1)
        for offset, p in enumerate(procs[start:start + rows]):
            index = start + offset
            label = f"{p['pid']:7} {p['cpu']:6.1f} {size(p['rss']):>6}  {p['name']}"
            self.text(y + 1 + int(header) + offset, x + 1, label.ljust(w - 2), w - 2, curses.A_REVERSE if index == self.selected else 0)
        if not procs:
            self.text(y + 1, x + 2, 'No matching processes', w - 4)
        return procs[self.selected] if procs else None

    def power_menu(self, y, x, h, w):
        self.box(y, x, h, w, 'POWER CONTROLS', self.colors[3])
        rows = max(0, h - 2)
        start = max(0, self.action - rows + 1)
        for offset, (label, _) in enumerate(ACTIONS[start:start + rows]):
            index = start + offset
            self.text(y + 1 + offset, x + 1, ('› ' + label).ljust(w - 2), w - 2, curses.A_REVERSE if index == self.action else 0)

    def external(self, command):
        curses.def_prog_mode()
        curses.endwin()
        try:
            result = subprocess.run(command, check=False)
            self.message = f'Command exited {result.returncode}'
            if command[0] != 'btop':
                input('\nPress Enter to return to psave... ')
        except (OSError, EOFError, KeyboardInterrupt) as error:
            self.message = str(error) or 'Cancelled'
        finally:
            curses.reset_prog_mode()
            self.win.clear()
        self.metrics.last_time = None
        self.metrics.last_cpu.clear()
        self.metrics.last_net = self.metrics.last_io = None
        self.metrics.energy.clear()
        self.metrics.profile_due = 0

    def overlay(self, title, lines):
        h, w = self.win.getmaxyx()
        bw = max(10, min(w - 2, 76))
        wrapped = []
        for line in lines:
            while len(line) > bw - 4:
                wrapped.append(line[:bw - 4])
                line = line[bw - 4:]
            wrapped.append(line)
        bh = min(h - 2, len(wrapped) + 2)
        top, left = (h - bh) // 2, (w - bw) // 2
        for row in range(top, top + bh):
            self.text(row, left, ' ' * bw, bw)
        self.box(top, left, bh, bw, title, self.colors[3])
        for offset, line in enumerate(wrapped[:bh - 2]):
            self.text(top + 1 + offset, left + 2, line, bw - 4)

    def draw(self):
        self.win.erase()
        h, w = self.win.getmaxyx()
        m = self.metrics
        if w < 28 or h < 8:
            self.text(0, 0, 'psave: use at least 28x8')
            self.text(1, 0, 'q: quit')
            self.win.refresh()
            return
        tabs = ['Dashboard', 'Processes', 'Power']
        header = f' PSAVE  {" | ".join(f"{i+1}:{name}" for i,name in enumerate(tabs))}' if w >= 64 else f' PSAVE | {tabs[self.tab]} | Tab →'
        self.text(0, 0, header.ljust(w), w, self.colors[0] | curses.A_BOLD)
        batt = f'{m.capacity:.0f}%' if m.capacity is not None else '?'
        watts = f'{m.watts:.1f}W' if m.watts is not None else '--W'
        if w >= 75:
            summary = f' CPU {m.cpu:4.1f}%  RAM {size(m.mem_used)}/{size(m.mem_total)}  BAT {batt} {watts}  FREE {size(m.disk.free)}  {m.profile}'
        else:
            summary = f' CPU {m.cpu:.0f}% RAM {m.ram:.0f}% BAT {batt} {watts} FREE {size(m.disk.free)}'
        self.text(1, 0, summary, w)
        content_h = h - 4
        if self.tab == 1:
            self.processes(2, 0, content_h, w)
        elif self.tab == 2:
            if w >= 68 and content_h >= 10:
                left = w // 2
                self.power_menu(2, left, content_h, w - left)
                upper = max(5, content_h // 2)
                self.chart(2, 0, upper, left, 'BATTERY 0–100%', 'battery', f'{batt} · {m.status}', self.colors[1])
                scale = max(10, max((v for v in m.history['watts'] if v is not None), default=0) * 1.1)
                self.chart(2 + upper, 0, content_h - upper, left, f'POWER 0–{scale:.0f}W', 'watts', f'{watts} · screen {brightness()}%', self.colors[3], scale)
            else:
                self.power_menu(2, 0, content_h, w)
        elif w >= 68 and content_h >= 17:
            top_h = min(8, max(5, content_h // 3))
            lower_h = 5 if content_h >= 22 else 4
            left = w // 2
            self.chart(2, 0, top_h, left, 'CPU 0–100%', 'cpu', f'{m.cpu:.1f}% · {len(m.cores)} cores', self.colors[0])
            self.chart(2, left, top_h, w - left, 'MEMORY 0–100%', 'ram', f'{size(m.mem_used)} / {size(m.mem_total)} · {m.ram:.0f}%', self.colors[2])
            scale = max(10, max((v for v in m.history['watts'] if v is not None), default=0) * 1.1)
            self.chart(2 + top_h, 0, lower_h, left, f'POWER 0–{scale:.0f}W', 'watts', f'{watts} · battery {batt} · {m.status}', self.colors[3], scale)
            net_scale = max(1024, max(m.history['net'], default=0) * 1.1)
            self.chart(2 + top_h, left, lower_h, w - left, 'NETWORK', 'net', f'↓ {size(m.rx)}/s ↑ {size(m.tx)}/s  IO {size(m.io)}/s', self.colors[4], net_scale)
            self.processes(2 + top_h + lower_h, 0, content_h - top_h - lower_h, w)
        else:
            chart_h = min(5, max(3, content_h // 3)) if content_h >= 6 else 1
            charts = [
                ('CPU 0–100%', 'cpu', f'{m.cpu:.1f}% · RAM {m.ram:.0f}%', self.colors[0], 100),
                ('MEMORY 0–100%', 'ram', f'{size(m.mem_used)} / {size(m.mem_total)}', self.colors[2], 100),
                ('POWER', 'watts', watts, self.colors[3], max(10, max((v for v in m.history['watts'] if v is not None), default=0) * 1.1)),
                ('NETWORK', 'net', f'↓ {size(m.rx)}/s ↑ {size(m.tx)}/s', self.colors[4], max(1024, max(m.history['net'], default=0) * 1.1)),
                ('BATTERY 0–100%', 'battery', f'{batt} · {m.status}', self.colors[1], 100),
                ('DISK IO', 'io', f'{size(m.io)}/s read + write', self.colors[4], max(1024, max(m.history['io'], default=0) * 1.1)),
            ]
            title, metric, label, color, ceiling = charts[self.compact_graph]
            if chart_h == 1:
                self.graph(2, 0, 1, w, m.history[metric], ceiling, color)
            else:
                self.chart(2, 0, chart_h, w, title, metric, label, color, ceiling)
            self.processes(2 + chart_h, 0, content_h - chart_h, w)
        if self.filtering:
            footer = '/' + self.query + '  [Enter done / Esc cancel]'
        else:
            footer = self.message
            if w < 68 or content_h < 17:
                footer = f'[{["CPU", "RAM", "POWER", "NET", "BAT", "IO"][self.compact_graph]}] g:next graph | ' + footer
        self.text(h - 2, 0, (' PAUSED | ' if self.paused else ' ') + footer, w, curses.A_DIM)
        keys = ' Tab views · ↑↓ select · / filter · c/m sort · Enter details · t end · p power · b btop · q quit' if w >= 90 else ' Tab view ↑↓ select / find t end ? help q quit'
        self.text(h - 1, 0, keys, w, self.colors[0])
        if self.help:
            self.overlay('KEYS', ['Tab / 1 / 2 / 3: dashboard / processes / power', 'Up/Down or j/k: select process or power action', 'c: sort CPU (one core = 100%) | m: sort memory', '/: filter process name/PID | Esc: clear filter', 'Enter: process details or run power action', 't: end selected owned process (asks first)', 'g: cycle compact CPU/RAM/power/network/battery/IO graph', 's: school mode | r: restore saved settings', '[ / ]: brightness down/up | b: open installed btop', 'Space: pause | + / -: faster/slower (1–5 seconds)', 'Braille graphs: 2 samples/column, newest on right.', 'Power --W means no reading; q quits, ? closes help.'])
        elif self.confirm:
            p = self.confirm
            self.overlay('END PROCESS?', [f"PID {p['pid']}: {p['name']}", 'SIGTERM asks it to exit; unsaved work could be lost.', 'y: send SIGTERM | any other key: cancel'])
        elif self.details:
            p = self.details
            command = read(f"/proc/{p['pid']}/cmdline").replace('\0', ' ')
            self.overlay('PROCESS DETAILS', [f"PID {p['pid']}  {p['name']}  state={p['state']}", f"CPU {p['cpu']:.1f}%  RAM {size(p['rss'])}  UID {p['uid']}", command or '(command unavailable)', 'Press any key to close.'])
        self.win.refresh()

    def key(self, key):
        if self.confirm:
            target, self.confirm = self.confirm, None
            if key == ord('y'):
                self.terminate(target)
            return True
        if self.details:
            self.details = None
            return True
        if self.help:
            self.help = False
            return True
        if self.filtering:
            if key in (10, 13):
                self.filtering = False
            elif key == 27:
                self.filtering, self.query = False, ''
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                self.query = self.query[:-1]
            elif 32 <= key < 127:
                self.query += chr(key)
            self.selected, self.selected_pid = 0, None
            return True
        if key in (ord('q'), ord('Q')):
            return False
        if key in (9, ord('1'), ord('2'), ord('3'), ord('p')):
            self.tab = (self.tab + 1) % 3 if key == 9 else 2 if key == ord('p') else key - ord('1')
        elif key in (curses.KEY_UP, ord('k'), curses.KEY_DOWN, ord('j')):
            delta = -1 if key in (curses.KEY_UP, ord('k')) else 1
            if self.tab == 2:
                self.action = (self.action + delta) % len(ACTIONS)
            else:
                self.selected = max(0, min(len(self.visible_processes()) - 1, self.selected + delta))
                self.selected_pid = None
        elif key in (ord('c'), ord('m')):
            self.sort = 'cpu' if key == ord('c') else 'rss'
            self.selected, self.selected_pid = 0, None
        elif key == ord('/'):
            self.filtering = True
        elif key == 27:
            self.query = ''
        elif key == ord('?'):
            self.help = True
        elif key == ord('g'):
            self.compact_graph = (self.compact_graph + 1) % 6
        elif key == ord(' '):
            self.paused = not self.paused
        elif key in (ord('+'), ord('='), ord('-')):
            self.metrics.interval = min(5, max(1, self.metrics.interval + (1 if key == ord('-') else -1)))
            self.message = f'Refresh every {self.metrics.interval}s; graph column = {self.metrics.interval * 2}s'
        elif key in (ord('s'), ord('r'), ord('['), ord(']'), ord('b')):
            command = {ord('s'): ['school'], ord('r'): ['restore'], ord('['): ['dim', str(max(1, brightness() - 10))], ord(']'): ['dim', str(min(100, brightness() + 10))], ord('b'): ['btop']}[key]
            self.external(['btop'] if command == ['btop'] else [HELPER, *command])
        elif key in (10, 13, curses.KEY_ENTER) and self.tab == 2:
            _, command = ACTIONS[self.action]
            if isinstance(command, str):
                command = ['dim', str(max(1, min(100, brightness() + (-10 if command == 'dim-down' else 10))))]
            self.external(['btop'] if command == ['btop'] else [HELPER, *command])
        elif key in (10, 13, curses.KEY_ENTER, ord('t')) and self.tab != 2:
            procs = self.visible_processes()
            if procs:
                target = procs[min(self.selected, len(procs) - 1)]
                if key == ord('t'):
                    if target['uid'] != os.getuid() or target['pid'] in (1, os.getpid(), os.getppid()):
                        self.message = 'Can only end other processes owned by you.'
                    else:
                        self.confirm = target.copy()
                else:
                    self.details = target.copy()
        return True

    def terminate(self, target):
        # pidfd pins identity, avoiding PID reuse between confirmation and signal.
        try:
            fd = os.pidfd_open(target['pid'])
            try:
                current = proc_info(target['pid'])
                if not current or current['start'] != target['start'] or current['uid'] != os.getuid():
                    self.message = 'Process exited or changed; no signal sent.'
                    return
                signal.pidfd_send_signal(fd, signal.SIGTERM)
                self.message = f"Sent SIGTERM to {target['pid']} ({target['name']})"
            finally:
                os.close(fd)
        except (OSError, AttributeError) as error:
            self.message = f'Could not end process: {error}'

    def run(self):
        due = 0
        while True:
            now = time.monotonic()
            if now >= due and not self.paused:
                self.metrics.sample()
                due = now + self.metrics.interval
            self.draw()
            key = self.win.getch()
            if key != -1 and not self.key(key):
                return


if __name__ == '__main__':
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        sys.exit('Open psave in a terminal, or use psave help.')
    try:
        curses.wrapper(lambda win: UI(win).run())
    except KeyboardInterrupt:
        pass
    except curses.error as error:
        sys.exit(f'Terminal error: {error}. Try TERM=xterm-256color psave tui')
