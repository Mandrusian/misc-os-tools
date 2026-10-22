# `sway-edge-snap.py`

Background helper for Sway/SwayFX that snaps floating windows to half-screen or corner layouts when dragged near screen edges.

## Requirements

Python 3, a running Sway/SwayFX session, and `swaymsg` in `PATH`.

## Usage

```sh
python3 sway-edge-snap.py
```

Start it from your compositor autostart if desired. It runs until stopped. Tune `EDGE`, `POLL`, and `COOLDOWN` near the top of the script. It only adjusts floating containers and uses Sway's reported workspace rectangle.
