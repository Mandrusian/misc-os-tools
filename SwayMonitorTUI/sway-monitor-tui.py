#!/usr/bin/env python3
"""External monitor settings TUI for Sway and SwayFX.

Only external outputs are listed for individual editing; internal eDP/LVDS/DSI
panels are used as layout anchors when available.
Requires Python 3, curses (standard library), and swaymsg. No root required.
"""
import curses
import json
import shutil
import subprocess
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config/sway"
CONFIG_FILE = CONFIG_DIR / "monitors.conf"
MAIN_CONFIG = CONFIG_DIR / "config"
INTERNAL_PREFIXES = ("eDP-", "LVDS-", "DSI-")
SCALE_OPTIONS = ("0.5", "0.75", "1", "1.25", "1.5", "1.75", "2", "2.5", "3")


def command(*args, check=True):
    proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode:
        raise RuntimeError(proc.stderr.strip() or f"Command failed: {' '.join(args)}")
    return proc.stdout.strip()


def get_outputs():
    return json.loads(command("swaymsg", "-t", "get_outputs", "-r"))


def external_outputs():
    return [o for o in get_outputs() if o.get("name") and not o["name"].startswith(INTERNAL_PREFIXES)]


def mode_label(mode):
    hz = mode.get("refresh", 0) / 1000
    return f'{mode.get("width", "?")}x{mode.get("height", "?")} @ {hz:.3g} Hz'


def choose(stdscr, title, options, selected=0):
    if not options:
        return None
    idx = max(0, min(selected, len(options) - 1))
    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        stdscr.addnstr(0, 2, title, max(1, w - 4), curses.A_BOLD)
        stdscr.addnstr(1, 2, "↑/↓ or j/k move · Enter select · q/Esc back", max(1, w - 4))
        visible = max(1, h - 4)
        start = max(0, min(idx - visible + 1, len(options) - visible))
        for row, i in enumerate(range(start, min(len(options), start + visible)), 3):
            attr = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addnstr(row, 2, ("➤ " if i == idx else "  ") + str(options[i]), max(1, w - 4), attr)
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(options)
        elif key in (curses.KEY_ENTER, 10, 13):
            return idx
        elif key in (ord("q"), 27):
            return None


def message(stdscr, lines):
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    for i, line in enumerate(lines[:max(0, h - 2)], 1):
        stdscr.addnstr(i, 2, line, max(1, w - 4))
    stdscr.addnstr(h - 1, 2, "Press any key to return", max(1, w - 4))
    stdscr.refresh()
    stdscr.getch()


def save_output_settings(name, settings):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    old = CONFIG_FILE.read_text() if CONFIG_FILE.exists() else ""
    prefix = f"output {name} "
    lines = [line for line in old.splitlines() if not line.strip().startswith(prefix)]
    for key in ("mode", "scale", "position"):
        if settings.get(key):
            lines.append(f"output {name} {key} {settings[key]}")
    CONFIG_FILE.write_text("\n".join(lines).strip() + "\n")

    include_line = "include ~/.config/sway/monitors.conf"
    if MAIN_CONFIG.exists():
        main_text = MAIN_CONFIG.read_text()
        if include_line not in main_text and "include ~/.config/sway/*" not in main_text:
            with MAIN_CONFIG.open("a") as f:
                f.write("\n# Monitor settings managed by sway-monitor-tui\n" + include_line + "\n")
    command("swaymsg", "reload", check=False)


def setting_from_output(out):
    mode = out.get("current_mode") or {}
    rect = out.get("rect") or {}
    return {
        "mode": (f'{mode["width"]}x{mode["height"]}@{mode.get("refresh", 0) / 1000:.3f}Hz'
                 if mode.get("width") and mode.get("height") else ""),
        "scale": str(out.get("scale", 1)),
        "position": f'{rect.get("x", 0)} {rect.get("y", 0)}',
    }


def apply_setting(name, key, value):
    if key == "mode":
        command("swaymsg", "output", name, "mode", value)
    elif key == "scale":
        command("swaymsg", "output", name, "scale", value)
    elif key == "position":
        x, y = value.split()
        command("swaymsg", "output", name, "position", x, y)


def auto_arrange_outputs():
    """Place active external outputs in a row to the right of an internal/primary output.

    Sway's rect dimensions are logical pixels, so this also handles mixed scaling.
    On desktop setups without an internal panel, keep the primary (or first) output
    as the anchor and arrange the remaining outputs to its right.
    """
    outputs = [o for o in get_outputs() if o.get("active", True) and o.get("name")]
    if len(outputs) < 2:
        raise RuntimeError("Enable at least two monitors before arranging them.")

    internal = [o for o in outputs if o["name"].startswith(INTERNAL_PREFIXES)]
    if internal:
        anchor = internal[0]
        targets = [o for o in outputs if not o["name"].startswith(INTERNAL_PREFIXES)]
    else:
        anchor = next((o for o in outputs if o.get("primary")), outputs[0])
        targets = [o for o in outputs if o["name"] != anchor["name"]]

    if not targets:
        raise RuntimeError("No active external monitor was found to arrange.")

    # Preserve Sway's output order, which is usually the most predictable order.
    anchor_rect = anchor.get("rect") or {}
    x = anchor_rect.get("x", 0) + anchor_rect.get("width", 0)
    y = anchor_rect.get("y", 0)
    arranged = []
    for target in targets:
        name = target["name"]
        apply_setting(name, "position", f"{x} {y}")
        arranged.append(name)
        refreshed = next((o for o in get_outputs() if o.get("name") == name), target)
        rect = refreshed.get("rect") or {}
        width = rect.get("width", 0)
        if not width:
            mode = refreshed.get("current_mode") or {}
            scale = float(refreshed.get("scale", 1) or 1)
            width = round(mode.get("width", 0) / scale)
        x += width


def edit_output(stdscr, out):
    name = out["name"]
    settings = setting_from_output(out)
    while True:
        labels = [
            f'Resolution / refresh: {mode_label(out.get("current_mode") or {})}',
            f'Scale factor: {settings["scale"]}x',
            f'Position: {settings["position"]}',
            "Save these settings for future logins",
            "Back to output list",
        ]
        pick = choose(stdscr, f"Settings for {name}", labels)
        if pick is None or pick == 4:
            return
        try:
            if pick == 0:
                modes = out.get("modes", [])
                mode_names = [mode_label(m) for m in modes]
                mi = choose(stdscr, f"Resolution / refresh for {name}", mode_names)
                if mi is None:
                    continue
                mode = modes[mi]
                hz = mode.get("refresh", 0) / 1000
                value = f'{mode["width"]}x{mode["height"]}@{hz:.3f}Hz'
                apply_setting(name, "mode", value)
                settings["mode"] = value
            elif pick == 1:
                options = list(SCALE_OPTIONS)
                if settings["scale"] not in options:
                    options.insert(0, settings["scale"] + " (current/custom)")
                si = choose(stdscr, f"Scale factor for {name}", options,
                            options.index(settings["scale"]) if settings["scale"] in options else 0)
                if si is None:
                    continue
                value = options[si].split()[0]
                apply_setting(name, "scale", value)
                settings["scale"] = value
            elif pick == 2:
                choices = ["Right of another monitor", "Left of another monitor",
                           "Keep current position", "Automatically arrange all monitors"]
                pi = choose(stdscr, f"Position {name}", choices)
                if pi is None:
                    continue
                if pi == 3:
                    auto_arrange_outputs()
                    message(stdscr, ["Monitors arranged automatically.",
                                     "Internal panels are used as the anchor when available.",
                                     "Use 'Save these settings' on each monitor to keep the layout."])
                    out = next((o for o in external_outputs() if o["name"] == name), out)
                    settings = setting_from_output(out)
                    continue

                fresh = get_outputs()
                current = next((o for o in fresh if o["name"] == name), out)
                others = [o for o in fresh if o["name"] != name and o.get("active", True)]
                if pi == 2:
                    pos = settings["position"]
                elif not others:
                    message(stdscr, ["No other active monitor was found.",
                                     "Connect or enable another monitor first."])
                    continue
                else:
                    anchor_labels = [
                        f'{o["name"]} — {o.get("rect", {}).get("width", "?")}x{o.get("rect", {}).get("height", "?")} at '
                        f'{o.get("rect", {}).get("x", 0)} {o.get("rect", {}).get("y", 0)}'
                        for o in others
                    ]
                    ai = choose(stdscr, f"Position {name} relative to…", anchor_labels)
                    if ai is None:
                        continue
                    anchor = others[ai]
                    rect = anchor.get("rect", {})
                    current_rect = current.get("rect", {})
                    anchor_w = rect.get("width", 0)
                    current_w = current_rect.get("width", 0)
                    if not current_w:
                        scale = float(settings["scale"] or 1)
                        current_w = round((current.get("current_mode") or {}).get("width", 0) / scale)
                    ax = rect.get("x", 0)
                    ay = rect.get("y", 0)
                    if pi == 0:
                        pos = f"{ax + anchor_w} {ay}"
                    else:
                        pos = f"{ax - current_w} {ay}"
                apply_setting(name, "position", pos)
                settings["position"] = pos
            elif pick == 3:
                save_output_settings(name, settings)
                message(stdscr, [f"Saved settings for {name}.", f"Config: {CONFIG_FILE}"])
                continue
            message(stdscr, [f"Applied to {name}.", f"Mode: {settings['mode'] or 'unchanged'}",
                              f"Scale: {settings['scale']}x", f"Position: {settings['position']}"])
            out = next((o for o in external_outputs() if o["name"] == name), out)
        except Exception as exc:
            message(stdscr, [f"Couldn't update {name}:", str(exc)])


def main(stdscr):
    curses.curs_set(0)
    while True:
        try:
            outs = external_outputs()
        except Exception as exc:
            message(stdscr, ["Couldn't query Sway outputs.", str(exc), "Run inside a Sway/SwayFX session."])
            return
        labels = [
            f'{o["name"]} — {mode_label(o.get("current_mode") or {})} · scale {o.get("scale", 1)}x'
            for o in outs
        ] + ["Refresh output list", "Auto arrange all active monitors", "Quit"]
        pick = choose(stdscr, "SwayFX monitor settings", labels)
        if pick is None or pick == len(labels) - 1:
            return
        if pick == len(outs):
            continue
        if pick == len(outs) + 1:
            try:
                auto_arrange_outputs()
                message(stdscr, ["Monitors arranged automatically.",
                                 "Internal panels are used as the anchor when available.",
                                 "Use 'Save these settings' on each monitor to keep the layout."])
            except Exception as exc:
                message(stdscr, ["Couldn't arrange monitors:", str(exc)])
            continue
        edit_output(stdscr, outs[pick])


if __name__ == "__main__":
    if not shutil.which("swaymsg"):
        print("swaymsg not found. Run this from inside Sway/SwayFX.", file=sys.stderr)
        sys.exit(1)
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
