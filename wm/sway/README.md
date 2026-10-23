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

### `swaym`

Restore output positions saved in `~/.config/sway/monitors.conf`, useful after a compositor reload. It does not hardcode monitor names or dimensions.

Install it for your user:

```sh
install -Dm755 wm/sway/swaym ~/.local/bin/swaym
```

Arrange your monitors correctly, then save their current positions:

```sh
swaym --save-current
```

Run `swaym` to reapply the saved positions. Ensure your Sway config includes `~/.config/sway/monitors.conf` so the layout also loads during compositor startup/reload. See [the full swaym guide](swaym.md).

## Runtime dependencies

Beyond SwayFX and Waybar, the config and Waybar click handlers may use these tools:

- Terminal: `foot`, `alacritty`
- Launcher: `wofi`
- Session/locking: `swayidle`, `swaylock`
- Brightness: `brightnessctl`
- System monitor: `btop`
- Network editor: `nm-connection-editor`
- Audio: `pavucontrol`, `pactl`, `wpctl` (WirePlumber CLI)
- Screenshot: `grimshot`
- Calendar: `cal`, `bash`
- Helper scripts: Python 3 and `swaymsg` (normally supplied with Sway/SwayFX)

Install only the tools you use; unused bindings and click actions can be removed from `config` or the Waybar configuration.
