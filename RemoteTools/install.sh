#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DEST=${XDG_BIN_HOME:-"$HOME/.local/bin"}
mkdir -p "$DEST"
for tool in "$HERE"/bin/*; do
    [ -f "$tool" ] || continue
    name=${tool##*/}
    install -m 0755 "$tool" "$DEST/$name"
done
printf 'Installed RemoteTools into %s\n' "$DEST"
printf 'Ensure %s is on PATH.\n' "$DEST"
