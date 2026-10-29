# System tools

Personal Linux utilities, with reusable paths and no bundled machine state.

```sh
./SystemTools/install.sh
```

This installs commands into `~/.local/bin` and psave's companion into
`~/.local/share/psave`. `XDG_BIN_HOME` and `XDG_DATA_HOME` override those paths.
Installation replaces commands with the same names; it does not edit your shell
startup files, install packages, or start daemons.

| Command | Purpose | Dependencies / scope |
|---|---|---|
| [`psave`](psave/README.md) | Battery controls and task manager with live graphs | Python 3, Bash, Fedora Asahi hardware, TuneD/PPD D-Bus API, brightnessctl |
| `asahi-battery` | GTK battery status window | Asahi `macsmc-battery`, Python GObject bindings, GTK 4, libadwaita, UPower |
| `avm` | Wrapper for ika Android VM setup and management | Fedora 44 ARM64/KVM, ika, curl, RPM/DNF; `setup` uses sudo |
| `get_distros` | Select and download OS images, optionally copy over SSH | Python curses, curl; SSH/scp for optional transfers |
| `install-pocketlink` | Find a PocketLink APK in Downloads and install over ADB | `/usr/bin/adb`, an authorized Android device |
| `larplist` | Show availability and examples for terminal decoration tools | Bash, a terminal; listed tools are optional |

`avm help` lists operations. `avm reset` erases Android VM data. Its backend
release and Fedora version are pinned in the script; review them before setup.

`get_distros` contains a snapshot of image URLs. Check the upstream release URLs
and verify image checksums before using downloads. Its distro selection screen
needs a tall terminal. Downloads are kept in `~/Downloads/isos`; no automatic
cleanup runs. An SSH host is entered explicitly for optional transfers.

`install-pocketlink` prefers the first matching PocketLink APK; if none is found,
it automatically chooses the newest APK in Downloads. It prints the selected
path and installs it with `adb install -r`. Check your Downloads contents before
running it.

Hyprland settings live in [`wm/hyprland`](../wm/hyprland/README.md); reusable Bash
aliases and prompt code live in [`ShellTools`](../ShellTools/README.md).
