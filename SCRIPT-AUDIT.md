# Local utility import audit

Reviewed shell startup references, `~/bin`, and `~/.local/bin` before importing
scripts. Compared names and file contents against the repository's current main
branch and existing remote work branch. Only selected source files and generic
examples are included; no full home directory, shell startup, runtime configs,
saved power settings, SSH material, logs, message history, or generated caches.

## Added categories

- `SystemTools`: psave and its companion TUI, Asahi GTK battery viewer, ika VM
  wrapper, image downloader, PocketLink APK installer, terminal-tool checklist.
- `ShellTools`: optional generic aliases and a Linux Bash prompt.
- `wm/hyprland`: `hsettings`, found via a shell alias.
- `RemoteTools`: missing rchat client/overlay/notification helpers and a generic
  config example, alongside the existing remote tools.

## Privacy and portability edits

- Removed an embedded overlay device identity; use configured identity or runtime
  hostname instead.
- Replaced a personal SSH alias example with a generic alias.
- Removed an absolute per-user psave launcher assumption; support adjacent source
  files and XDG installation directories.
- Removed the APK installer's device-brand assumption and per-user launcher path.
- Removed the terminal checklist's embedded hostname display and local chat-history
  instructions.
- Used subprocess argument arrays for downloader/transfer commands and rchat's
  notification viewer; user input is no longer interpolated into a local shell.
- Commit author uses the existing public GitHub noreply identity rather than a
  locally configured private email address.

Checked imported text for credential/private-key patterns, account names, private
addresses, email addresses, absolute home paths and machine identifiers. Runtime
paths based on `$HOME` or `Path.home()` remain where they are part of tool behavior.

## Skipped

| Local items | Reason |
|---|---|
| `gh-push`, `sway-monitor-tui` | Already published; identical source exists |
| `pipe_isos`, `rclip`, `rfiles`, `rlogin`, `rsch`, `rscr`, `rscr-viewer`, `rspy`, `rtui`, `rwake` | Already published; kept repository versions rather than importing machine-specific local variants |
| `sway-edge-snap.py`, `sway-swipe-ws`, `swayshortcuts`, older `sway-monitor-tui.py` | Existing Sway tools or older variants; no duplicate import |
| `swaym` | Already on the existing remote work branch; local layout is machine-specific |
| `rsys` | Embedded private SSH target and host-specific administrative/session actions; remains excluded as documented in RemoteTools |
| Asahi-suite symlinks and compiled programs | Belong to separate projects; no binary or duplicate-source import |
| Python package entry points, `vba_extract.py`, aquarium launchers | Installed third-party utilities |
| `bigfetch`, `flagwave`, `glassicon`, `horizon-asahi`, application launchers | Wrappers depend on separate application/config/asset trees |
| `*.backup*`, full `.bashrc`, application/game launch aliases | Old variants or personal shell setup |

The original local scripts and the existing checkout's unresolved merge are left
unchanged. Validation covers packaging, parsing and offline behavior; GUI,
hardware, backend downloads and live remote interactions are not exercised.
