# Sway tools

Utilities and configuration files specific to the Sway/SwayFX window manager. These are kept separate from SSH and remote-host utilities in [`RemoteTools/`](../../RemoteTools/).

## Tools

| Tool | Purpose | Guide |
|---|---|---|
| [`sway-edge-snap.py`](sway-edge-snap.py) | Snap floating windows near screen edges | [Guide](docs/sway-edge-snap.py.md) |
| [`sway-swipe-ws`](sway-swipe-ws) | Move to the next or previous workspace | [Guide](docs/sway-swipe-ws.md) |
| [`swayshortcuts`](swayshortcuts) | List key bindings from user Sway config | [Guide](docs/swayshortcuts.md) |
| [`swaym`](swaym) | Save and reapply output positions (`monitors.conf`) | [Guide](docs/swaym.md) |

## Config & installer

- [`config`](config) — floating monochrome Sway/SwayFX configuration.
- [`waybar/`](waybar/config.jsonc) — Waybar configuration (`config.jsonc`, `style.css`, and `cal.sh` calendar popup helper).
- [`install.sh`](install.sh) — distro-aware installer that installs SwayFX/Waybar, backs up `~/.config/sway` and `~/.config/waybar`, copies the configs, and installs the Sway helper scripts into `~/.local/bin`.

Review [`config`](config), [`waybar/config.jsonc`](waybar/config.jsonc), and [`install.sh`](install.sh) before installing.

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
