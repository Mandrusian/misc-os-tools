# `rclip`

Copy bytes from standard input into the clipboard of a remote Linux desktop. Clipboard data is base64-transported over SSH and is **not interpolated into a shell script**.

## Requirements

- Python 3 and OpenSSH client locally
- Python 3, `wl-copy`, `pgrep`, and an active Wayland session remotely
- An SSH alias in `~/.ssh/config`

## Usage

```sh
printf 'hello from this machine' | rclip my-host
cat notes.txt | rclip my-host
```

The remote process searches common compositor process names for session environment variables. Desktop configurations that do not expose these variables through the compositor process may need a session-specific adjustment. Empty input is rejected.
