#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DEST=${XDG_BIN_HOME:-"$HOME/.local/bin"}
DATA=${XDG_DATA_HOME:-"$HOME/.local/share"}
mkdir -p "$DEST" "$DATA/psave"
install -m 0755 "$HERE/psave" "$DEST/psave"
install -m 0644 "$HERE/tui.py" "$DATA/psave/tui.py"
printf 'Installed psave. Run psave help or psave in a terminal.\n'
