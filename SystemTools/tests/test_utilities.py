"""Offline packaging and behavior checks; no real power or network operations."""
import ast
import fcntl
import importlib.util
import os
from pathlib import Path
import pty
import select
import signal
import struct
import subprocess
import tempfile
import termios
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]


class UtilitiesTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='utilities test ')
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.env = {**os.environ, 'HOME': str(self.home),
                    'XDG_BIN_HOME': str(self.home / 'custom bin'),
                    'XDG_DATA_HOME': str(self.home / 'custom data'),
                    'XDG_STATE_HOME': str(self.home / 'state')}

    def run_command(self, command, **kwargs):
        return subprocess.run(command, env=self.env, capture_output=True, text=True,
                              check=True, timeout=10, **kwargs)

    def install(self):
        self.run_command([str(ROOT / 'SystemTools/install.sh')])
        return Path(self.env['XDG_BIN_HOME']) / 'psave'

    def test_imported_sources_parse(self):
        paths = list((ROOT / 'SystemTools').rglob('*'))
        paths += list((ROOT / 'ShellTools').rglob('*'))
        paths += list((ROOT / 'wm/hyprland').rglob('*'))
        paths += list((ROOT / 'RemoteTools/bin').iterdir())
        for path in paths:
            if not path.is_file() or '__pycache__' in path.parts:
                continue
            text = path.read_text()
            if path.suffix == '.py' or text.startswith('#!/usr/bin/env python'):
                ast.parse(text, filename=str(path))
            elif path.suffix in ('.sh', '.bash') or 'bash' in text.splitlines()[0] or text.startswith('#!/bin/sh'):
                self.run_command(['bash', '-n', str(path)])

    def test_install_with_spaces_and_custom_xdg_paths(self):
        helper = self.install()
        self.assertTrue(helper.is_file())
        self.assertTrue((Path(self.env['XDG_DATA_HOME']) / 'psave/tui.py').is_file())
        self.assertIn('task manager', self.run_command([str(helper), 'help']).stdout)
        result = subprocess.run([str(helper), 'tui'], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Open psave in a terminal', result.stderr)
        self.assertFalse((self.home / '.bashrc').exists())
        self.assertFalse((self.home / '.local/bin').exists())

    def test_school_restore_uses_saved_settings(self):
        helper = self.install()
        mock_bin = self.home / 'mocks'
        mock_bin.mkdir()
        mock = '''#!/usr/bin/env python3
from pathlib import Path
import os, sys
root = Path(os.environ['MOCK_POWER'])
if Path(sys.argv[0]).name == 'busctl':
    path = root/'profile'
    if 'set-property' in sys.argv:
        path.write_text(sys.argv[-1])
    else:
        print('s "' + path.read_text() + '"')
else:
    name, operation = sys.argv[2:4]
    path = root/name
    if operation == 'get': print(path.read_text())
    elif operation == 'max': print(500 if name == 'apple-panel-bl' else 255)
    elif operation == 'set':
        value = sys.argv[4]
        path.write_text(str(int(value[:-1])*5) if value.endswith('%') else value)
'''
        for name in ('busctl', 'brightnessctl'):
            path = mock_bin / name
            path.write_text(mock)
            path.chmod(0o755)
        fixture = self.home / 'power'
        fixture.mkdir()
        for name, value in [('profile', 'balanced'), ('apple-panel-bl', '325'), ('kbd_backlight', '94')]:
            (fixture / name).write_text(value)
        self.env.update(MOCK_POWER=str(fixture), PATH=str(mock_bin) + os.pathsep + os.environ['PATH'])
        self.run_command([str(helper), 'school'])
        self.assertEqual((fixture / 'profile').read_text(), 'power-saver')
        self.assertEqual((fixture / 'apple-panel-bl').read_text(), '175')
        self.assertEqual((fixture / 'kbd_backlight').read_text(), '0')
        # Re-entering school mode must not overwrite the original settings.
        self.run_command([str(helper), 'school'])
        self.run_command([str(helper), 'restore'])
        for name, value in [('profile', 'balanced'), ('apple-panel-bl', '325'), ('kbd_backlight', '94')]:
            self.assertEqual((fixture / name).read_text(), value)

    def test_remote_help_does_not_create_state(self):
        for name in ('rchat', 'notifs'):
            result = self.run_command(['python3', str(ROOT / 'RemoteTools/bin' / name), '--help'])
            self.assertIn('usage:', result.stdout)
        self.assertFalse((self.home / '.rchat').exists())
        self.assertFalse((self.home / '.config').exists())

    def test_compact_and_full_dashboard(self):
        for rows, cols in [(24, 80), (12, 40), (8, 28)]:
            with self.subTest(size=(cols, rows)):
                master, slave = pty.openpty()
                fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
                process = subprocess.Popen([str(ROOT / 'SystemTools/psave/psave')],
                                           stdin=slave, stdout=slave, stderr=slave,
                                           env={**self.env, 'TERM': 'xterm-256color'})
                os.close(slave)
                output = bytearray()
                def collect(duration):
                    deadline = time.monotonic() + duration
                    while time.monotonic() < deadline:
                        if select.select([master], [], [], .02)[0]:
                            try:
                                output.extend(os.read(master, 65536))
                            except OSError:
                                return
                try:
                    deadline = time.monotonic() + 4
                    while b'PROCES' not in output and time.monotonic() < deadline:
                        collect(.1)
                    self.assertIn(b'PROCES', output)
                    self.assertTrue(any(0x2800 <= ord(c) <= 0x28ff for c in output.decode(errors='ignore')))
                    os.write(master, b'g2m/python\n')
                    collect(.15)
                    os.write(master, b'\x1b3')
                    collect(.15)
                    fcntl.ioctl(master, termios.TIOCSWINSZ, struct.pack('HHHH', 16, 48, 0, 0))
                    process.send_signal(signal.SIGWINCH)
                    collect(.15)
                    os.write(master, b'q')
                    process.wait(timeout=4)
                    collect(.05)
                    self.assertEqual(process.returncode, 0, output.decode(errors='replace'))
                    self.assertNotIn(b'Traceback', output)
                finally:
                    if process.poll() is None:
                        process.kill()
                    process.wait()
                    os.close(master)


if __name__ == '__main__':
    unittest.main()
