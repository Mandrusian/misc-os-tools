# `rwake`

Send best-effort display wake and session-unlock commands to a remote Linux desktop over SSH.

## Requirements

OpenSSH client locally; remote `bash`, `pgrep`, and the applicable desktop tools. A configured SSH alias is required.

## Usage

```sh
rwake my-host
```

Support depends on the remote compositor, desktop environment, permissions, and whether a graphical session is running. This is not a login bypass and cannot unlock every screen locker.
