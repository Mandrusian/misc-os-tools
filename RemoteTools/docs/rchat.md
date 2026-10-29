# rchat and notification helpers

An SSH-based chat client with an optional desktop overlay and notification
inspection. No peer identities, addresses, logs, or live configurations are bundled.

```sh
./RemoteTools/install.sh
mkdir -p ~/.config/rchat
# Only copy if you do not already have a config:
cp -n RemoteTools/examples/rchat-config.json ~/.config/rchat/config.json
```

Edit `me`, peer names and each peer's `host` to use your own SSH aliases. The
configured remote command is executed over SSH: only use configurations you
control. Install `rchat` at both ends, and ensure it is on the non-interactive SSH
PATH. Peers need the corresponding configuration to receive messages.

| Command | Purpose | Dependencies |
|---|---|---|
| `rchat` | Chat TUI; `/to NAME`, `/peers`, `/quit` | Python curses, SSH, `notify-send` for received desktop notifications |
| `rchat --send workstation 'hello'` | Send a message to a configured peer | Same; sends over SSH when invoked |
| `rchat --clear` | Ask the local overlay to clear cards | Python 3 |
| `rchat-notifyd` | Show incoming messages as desktop overlay cards | PyQt6, graphical session; Qt layer-shell integration for Wayland |
| `rchat-sysnotifyd` | Explicitly capture desktop notification events locally | Python 3, `dbus-monitor`, `stdbuf`, session bus |
| `notifs --past` | Show locally received messages and configured peers' notifications | Python 3, SSH for remote inspection |
| `notifs --active-only --no-sys` | Show active chat overlays only | Same |

The daemon commands stay in the foreground until stopped; nothing auto-starts.
`rchat-sysnotifyd` records notification app names, summaries and bodies under
`~/.rchat/system-notifications.jsonl`. Only run it when you want that history.
Messages and overlay state are also local files under `~/.rchat`; keep them private.
Remote notification queries explicitly use the peers in your configuration.

No live messages, notifications, SSH connections, or desktop daemons are started
by the installers or offline tests.
