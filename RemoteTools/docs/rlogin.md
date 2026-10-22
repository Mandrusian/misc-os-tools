# `rlogin`

Open an interactive SSH session to a configured host alias. It deliberately does not try to unlock the remote screen, type passwords, or bypass a login manager.

## Requirements

OpenSSH client and an SSH alias in `~/.ssh/config`.

## Usage

```sh
rlogin my-host
```

SSH authentication and host-key verification follow your normal OpenSSH configuration.
