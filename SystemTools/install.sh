#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DEST=${XDG_BIN_HOME:-"$HOME/.local/bin"}
mkdir -p "$DEST"
for tool in "$HERE"/bin/*; do
    install -m 0755 "$tool" "$DEST/${tool##*/}"
done
"$HERE/psave/install.sh"
printf 'Installed SystemTools into %s. Ensure it is on PATH.\n' "$DEST"
