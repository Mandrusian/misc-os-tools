#!/bin/sh
# Lightweight offline checks for the scripts in bin/.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BIN="$HERE/bin"
python3 - "$BIN" <<'PY'
import ast, pathlib, sys
root = pathlib.Path(sys.argv[1])
for path in root.iterdir():
    if not path.is_file():
        continue
    text = path.read_text(errors="replace")
    if path.suffix == ".py" or text.startswith("#!/usr/bin/env python"):
        ast.parse(text, filename=str(path))
print("Python syntax checks passed")
PY
sh -n "$BIN/sway-swipe-ws"
python3 "$BIN/swayshortcuts" --help >/dev/null
python3 "$BIN/rsch" --list >/dev/null
printf '%s\n' 'Smoke checks passed.'
