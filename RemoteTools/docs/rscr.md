# `rscr` and `rscr-viewer`

Stream a remote Wayland desktop to a local PyQt6 window. `rscr-viewer` is a required companion executable and must be installed beside `rscr`.

## Requirements

- Locally: Python 3, OpenSSH client, PyQt6
- Remotely: Python 3, `grim`, `pgrep`, and an active Wayland session
- A configured SSH alias

## Usage

```sh
rscr my-host
```

Close the viewer or press Ctrl+C to stop. The stream uses SSH and does not open a VNC port. Frame capture is uncompressed PNG and may use substantial bandwidth/CPU. It is not intended for unattended capture; only use it on machines and sessions you are authorized to view.
