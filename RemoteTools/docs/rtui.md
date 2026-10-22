# `rtui`

Small curses menu for launching the bundled remote tools against one SSH alias.

## Requirements

Python 3, curses (usually included with Python), and the `RemoteTools/bin` scripts installed on `PATH`. Individual tools have their own dependencies.

## Usage

```sh
rtui my-host
```

Use Up/Down or `j`/`k`, Enter to launch, and `q` to quit. The menu runs the selected tool as a separate process; options and behavior are documented in each tool's README.
