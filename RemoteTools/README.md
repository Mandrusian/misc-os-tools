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

3. Check the per-tool guide under [`docs/`](docs/). Each guide lists dependencies, usage, and important limitations.

## Tools

| Tool | Purpose | Guide |
|---|---|---|
| `pipe_isos` | Stream a local directory to remote home | [README](docs/pipe_isos.md) |
| `rclip` | Pipe stdin to remote Wayland clipboard | [README](docs/rclip.md) |
| `rfiles` | Remote file browser and transfer UI | [README](docs/rfiles.md) |
| `rlogin` | Interactive SSH login | [README](docs/rlogin.md) |
| `rsch` | Local or remote screenshot capture | [README](docs/rsch.md) |
| `rscr` | Remote Wayland screen stream | [README](docs/rscr.md) |
| `rscr-viewer` | GUI companion for `rscr` | [README](docs/rscr-viewer.md) |
| `rspy` | KDE Plasma VNC via SSH tunnel | [README](docs/rspy.md) |
| `rtui` | Curses launcher for remote tools | [README](docs/rtui.md) |
| `rwake` | Best-effort remote display wake | [README](docs/rwake.md) |

The Sway/SwayFX-specific tools live separately in [`wm/sway/`](../wm/sway/). The `SwayMonitorTUI` utility is maintained in [`SwayMonitorTUI/`](../SwayMonitorTUI/).

The `rsys` diagnostic/admin TUI is intentionally not published in this pass because it contains machine-specific administrative/session actions that need a separate safety review.

## Validation

Run `./RemoteTools/tests-smoke.sh` from the repository root (or `./tests-smoke.sh` from this directory) for offline syntax and smoke checks.

The Python scripts are syntax-checked with `ast.parse`/`py_compile`; shell scripts are checked with `sh -n`. GUI, SSH, desktop-session, and remote-host behavior still needs to be exercised on the relevant systems.
