# RemoteTools

A collection of SSH-based utilities for working with remote Linux hosts. Remote targets are supplied as SSH aliases, rather than embedding a personal hostname, IP address, username, or desktop-session path.

## Setup

1. Configure an SSH alias in `~/.ssh/config`, for example:

   ```sshconfig
   Host my-host
       HostName example.com
       User your-user
       IdentityFile ~/.ssh/id_ed25519
   ```

2. Install the scripts:

   ```sh
   ./RemoteTools/install.sh
   ```

3. Check each guide under [`docs/`](docs/) for dependencies, usage, and limitations.

## Tools

| Tool | Purpose | Guide |
|---|---|---|
| `pipe_isos` | Stream a local directory to remote home | [Guide](docs/pipe_isos.md) |
| `rclip` | Pipe stdin to remote Wayland clipboard | [Guide](docs/rclip.md) |
| `rfiles` | Remote file browser and transfer UI | [Guide](docs/rfiles.md) |
| `rlogin` | Interactive SSH login | [Guide](docs/rlogin.md) |
| `rsch` | Local or remote screenshot capture | [Guide](docs/rsch.md) |
| `rscr` | Remote Wayland screen stream | [Guide](docs/rscr.md) |
| `rscr-viewer` | GUI companion for `rscr` | [Guide](docs/rscr-viewer.md) |
| `rspy` | KDE Plasma VNC via SSH tunnel | [Guide](docs/rspy.md) |
| `rtui` | Curses launcher for remote tools | [Guide](docs/rtui.md) |
| `rwake` | Best-effort remote display wake | [Guide](docs/rwake.md) |

Sway/SwayFX-specific utilities live in [`wm/sway/`](../wm/sway/), not in this directory. The Sway Monitor TUI is documented in [`SwayMonitorTUI/`](../SwayMonitorTUI/).

The `rsys` diagnostic/admin TUI is intentionally not published in this pass because it contains machine-specific administrative/session actions that need a separate safety review.

## Validation

Run `./RemoteTools/tests-smoke.sh` from the repository root (or `./tests-smoke.sh` from this directory) for offline syntax and smoke checks. GUI, SSH, desktop-session, and remote-host behavior still needs testing on relevant systems.
