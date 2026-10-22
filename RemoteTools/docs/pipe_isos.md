# `pipe_isos`

Stream a local directory to a directory under the remote SSH user's home using a `tar`/SSH pipeline. Unlike `scp`, this does not create a local archive.

## Requirements

- Python 3, `tar`, and OpenSSH client locally
- `ssh` and `tar` remotely
- A working SSH alias configured in `~/.ssh/config`

## Usage

```sh
pipe_isos my-host                         # ~/Downloads/isos -> ~/isos
pipe_isos my-host ~/Downloads/images --destination backups/images
```

`--destination` must be a relative path under the remote home directory. Existing files with matching names may be overwritten. Review the source and destination before running.
