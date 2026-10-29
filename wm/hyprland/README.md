# Hyprland settings

`hsettings` provides a numbered terminal menu, an optional Rofi menu, and direct
commands for monitor scale/resolution, gaps, blur, rounding, borders and animations.

```sh
install -Dm755 wm/hyprland/hsettings ~/.local/bin/hsettings
hsettings help
hsettings status
hsettings scale 1.5
hsettings gaps 8
hsettings animations off
hsettings rofi
```

Requires Bash, `hyprctl` in an active Hyprland session, and `jq`. Rofi is needed
only for `rofi` mode; `notify-send` is optional. The Rofi theme defaults to
`~/.config/rofi/style.rasi` and can be overridden with `HSETTINGS_ROFI_THEME`.

Changes apply immediately and persist in `~/.config/hypr/settings.d/*.conf`.
The script appends include lines to `~/.config/hypr/hyprland.conf` when required;
review or back up your configuration before changing settings. `reset` empties
those override files, then reloads Hyprland.
