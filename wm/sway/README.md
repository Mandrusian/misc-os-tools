# Sway tools

Utilities specific to the Sway/SwayFX window manager. These are kept separate from SSH and remote-host utilities under `RemoteTools/`.

## Tools

### `sway-edge-snap.py`

Background helper that snaps floating windows to half-screen or corner layouts when dragged near screen edges.

**Requirements:** Python 3, a running Sway/SwayFX session, and `swaymsg` in `PATH`.

```sh
python3 wm/sway/sway-edge-snap.py
```

Start it from your compositor autostart if desired. It runs until stopped. Tune `EDGE`, `POLL`, and `COOLDOWN` near the top of the script.

### `sway-swipe-ws`

Move to the next or previous workspace in Sway's reported workspace list. Supports named as well as numbered workspaces.

**Requirements:** Sway/SwayFX, `swaymsg`, and Python 3.

```sh
wm/sway/sway-swipe-ws next
wm/sway/sway-swipe-ws prev
```

Bind these commands to your preferred gesture tool or key bindings; this script does not configure gestures itself.

### `swayshortcuts`

Generate a readable key-binding list from the current user's Sway configuration.

**Requirements:** Python 3. It reads config files and does not need a running Sway session.

```sh
wm/sway/swayshortcuts
wm/sway/swayshortcuts --config ~/.config/sway/config
wm/sway/swayshortcuts --raw
```

It follows `include` directives and reports `bindsym`/`bindcode` lines. It does not execute config commands, resolve all Sway variables, or fully interpret complex mode/block syntax; inspect the original config for ambiguous entries.
