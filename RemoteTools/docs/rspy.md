# `rspy`

Start or reuse a KDE Plasma `w0vncserver`, tunnel its localhost-only VNC port through SSH, and launch `vncviewer` locally.

## Requirements

- Locally: OpenSSH client and TigerVNC's `vncviewer`
- Remotely: KDE Plasma, `w0vncserver`, `pgrep`, and Python 3
- A configured SSH alias

## Usage

```sh
rspy my-host
rspy my-host --no-input
rspy my-host --fast
```

This helper is KDE/`w0vncserver`-specific. It uses a VNC server with no VNC-level authentication but binds it to remote localhost and relies on the SSH tunnel; do not remove `-localhost yes` from the server options. If a VNC server was already running, the script reuses it and will not stop it when exiting. If it starts the server, it attempts to stop that process on exit. Inspect `/tmp/w0vncserver-rspy.log` remotely if startup fails.
