# Bash helpers

Reusable pieces extracted from a shell setup. The complete `.bashrc`, application
launch commands, user paths, and machine-specific environment are not included.

- `aliases.bash`: shortcuts for editing/reloading `.bashrc`, editing Hyprland's
  config, and checking Hyprland errors. Editor shortcuts use `$EDITOR`, falling
  back to `micro`. Hyprland shortcuts need Hyprland.
- `prompt.sh`: three-line Bash prompt with CPU, memory, battery, load, Git status,
  and the previous exit code. Linux `/proc` and sysfs are required; Git is optional.
  Battery discovery includes standard `BAT*` devices and Asahi's macsmc device.

Copy the files to a location you choose and source them explicitly, for example:

```bash
mkdir -p ~/.config/bash
cp ShellTools/aliases.bash ShellTools/prompt.sh ~/.config/bash/
# Add either or both to ~/.bashrc:
source ~/.config/bash/aliases.bash
source ~/.config/bash/prompt.sh
```

Sourcing the prompt replaces `PROMPT_COMMAND` and `PS1`. Review it if you already
use another prompt or prompt hooks. No installer edits your shell startup files.
