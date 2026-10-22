# swaym — restore monitor positions

`swaym` reapplies output positions stored in `~/.config/sway/monitors.conf`. It is intended for Sway/SwayFX setups where output positions need to be restored after a compositor reload.

## Install for your user

From the repository root:

```sh
install -Dm755 wm/sway/swaym ~/.local/bin/swaym
```

Ensure `~/.local/bin` is on your `PATH`.

## Save your current layout

Arrange your monitors the way you want them, then run inside your Sway session:

```sh
swaym --save-current
```

This writes position rules for currently active outputs to `~/.config/sway/monitors.conf`. Review that file before relying on it.

## Restore the layout

```sh
swaym
```

The command applies only the saved position rules; it does not reload Sway or set resolutions/scales.

Ensure your main Sway config includes the saved file so positions are also applied during compositor startup/reload:

```sway
include ~/.config/sway/monitors.conf
```

Add that include once if it is not already covered by an existing include pattern. If another output-position rule conflicts with this file, fix the config ordering or duplicate rule.

## Safety and limitations

- Output names and positions are read from the live Sway output list when saving; no specific monitor names or dimensions are assumed.
- Review the generated config before using it, especially after changing monitor connections.
- Run from a terminal or key binding inside the Sway/SwayFX session.
