# `rsch`

Capture a screenshot locally or from an SSH host, save it in `~/.rsch`, update `~/.rsch/last.png`, and optionally open it.

## Requirements

- Python 3 and OpenSSH client
- For Linux/Wayland capture: `grim`; for KDE/X11 fallbacks: `spectacle`, `maim`, or `scrot` as applicable
- For macOS capture: the built-in `screencapture`
- A configured SSH alias for remote captures

## Usage

```sh
rsch                         # capture this machine
rsch local --open            # capture locally and open the result
rsch my-host --open          # capture remote host and open locally
rsch --list                  # list saved screenshots
```

Remote screenshots require an active, accessible graphical session. The script attempts to discover a Wayland socket but cannot guarantee capture from a locked or logged-out session.
