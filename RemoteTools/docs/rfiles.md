# `rfiles`

Curses-based remote file browser with previews and basic upload/download, rename, delete, and open actions.

## Requirements

- Python 3, OpenSSH client, `scp`, and a terminal supporting curses
- Python 3 on the remote host
- An SSH alias in `~/.ssh/config`

## Usage

```sh
rfiles my-host                 # start in remote home
rfiles my-host --start ~/Documents
```

Keys: arrows or `j`/`k` navigate; Enter opens directories; `d` downloads; `u` uploads; Delete removes the selected item after confirmation; `r` renames; `o` asks the remote desktop to open the selected file; `q` quits.

**Caution:** Delete is destructive (`rm -rf`) and acts on the selected remote path. Check the displayed host and path before confirming. Uploads/downloads use the current local directory.
