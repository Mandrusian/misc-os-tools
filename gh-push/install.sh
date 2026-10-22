#!/bin/sh
set -eu

SCRIPT_URL="https://raw.githubusercontent.com/Mandrusian/misc-os-tools/main/gh-push/gh-push"
if [ -n "${XDG_BIN_HOME:-}" ]; then
    BIN_DIR="$XDG_BIN_HOME"
else
    BIN_DIR="$HOME/.local/bin"
fi
DEST="$BIN_DIR/gh-push"
TMP_FILE="$(mktemp)"
trap 'rm -f "$TMP_FILE"' EXIT HUP INT TERM

if ! command -v curl >/dev/null 2>&1; then
    printf '%s\n' 'Error: curl is required to download gh-push.' >&2
    exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' 'Error: Python 3 is required.' >&2
    exit 1
fi
if ! command -v git >/dev/null 2>&1; then
    printf '%s\n' 'Error: Git is required.' >&2
    exit 1
fi

curl -fsSL "$SCRIPT_URL" -o "$TMP_FILE"
python3 - "$TMP_FILE" <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
compile(path.read_text(encoding="utf-8"), str(path), "exec")
PY
mkdir -p "$BIN_DIR"
install -m 755 "$TMP_FILE" "$DEST"
printf 'Installed gh-push to %s\n' "$DEST"
case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) printf 'Add %s to your PATH if it is not already there.\n' "$BIN_DIR" ;;
esac
printf '%s\n' 'Run gh-push from inside any Git repository.'
