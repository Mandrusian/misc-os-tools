# `swayshortcuts`

Generate a readable key-binding list from the current user's Sway configuration instead of assuming a particular set of shortcuts or applications.

## Requirements

Python 3. Reads config files only; it does not need a running Sway session.

## Usage

```sh
swayshortcuts
swayshortcuts --config ~/.config/sway/config
swayshortcuts --raw
```

It follows `include` directives and reports `bindsym`/`bindcode` lines. It does not execute config commands, resolve all Sway variables, or fully interpret complex mode/block syntax; inspect the original config for ambiguous entries.
