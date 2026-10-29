# psave

A battery helper and responsive Linux task manager, built with Bash and Python's
standard-library curses. Power controls target Fedora Asahi's `macsmc-battery`,
`apple-panel-bl`, `kbd_backlight`, and the TuneD/PPD D-Bus interface.

```sh
./SystemTools/psave/install.sh
psave
```

You can also run `./SystemTools/psave/psave` directly from this checkout. The
launcher finds its adjacent `tui.py`. No `.bashrc` changes are required when the
installation's bin directory is on PATH. Optional alias:

```bash
alias psave='"${XDG_BIN_HOME:-$HOME/.local/bin}/psave"'
```

## Dashboard

- Filled Braille CPU, RAM, power and network graphs, plus disk I/O rates.
- Live processes with per-process CPU (one core = 100%), resident memory and PID.
- Layouts from 28×8 through larger windows. Compact mode cycles all six graphs.
- Two-second sampling by default; no background monitoring after exit.

| Key | Action |
|---|---|
| `Tab`, `1`, `2`, `3` | Dashboard, processes, power controls |
| `↑` / `↓`, `j` / `k` | Select a process or power action |
| `g` | Cycle the compact CPU/RAM/power/network/battery/I/O graph |
| `/`, `Esc` | Filter by name/PID, clear filter |
| `c`, `m` | Sort by CPU or memory |
| `Enter` | Show process details or run selected power action |
| `t` | Ask to send SIGTERM to an owned process; `y` confirms |
| `s`, `r` | School mode, restore saved settings |
| `[`, `]` | Adjust brightness by 10% |
| `b` | Open btop if installed |
| `Space`, `+`, `-` | Pause, faster refresh, slower refresh |
| `?`, `q` | Help, quit |

SIGTERM can lose unsaved work. The process-end action checks ownership and uses a
PID file descriptor to avoid signalling a reused PID. Missing power readings are
shown as `--W`; discharge power can be estimated after 15 seconds of energy data.
Graphs fill while the dashboard is open; changing refresh rate affects future
samples without resampling older history.

## Commands

```sh
psave help
psave school       # Power saver, screen capped at 35%, keyboard light off
psave restore      # Restore profile and brightness saved before school mode
psave on           # Power-saver profile only
psave balanced
psave dim 25
psave status
psave top
psave bluetooth off
psave bluetooth on
psave suspend
psave install-tools  # Optional PowerTOP diagnostic; sudo/DNF
psave clean-system   # Rotate/trim system journal to 500 MB and clean DNF cache
```

School settings are saved locally under `${XDG_STATE_HOME:-~/.local/state}/psave`.
Repeated school-mode activation preserves the first saved settings. Power profile
changes persist until changed; your desktop may also adjust brightness. Bluetooth
is only changed by its explicit command, and Wi-Fi remains available.
