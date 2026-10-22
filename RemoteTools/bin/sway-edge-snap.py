#!/usr/bin/env python3
import json
import os
import subprocess
import time

EDGE = 24
POLL = 0.10
COOLDOWN = 0.8


def sway(*args):
    try:
        return subprocess.run(["swaymsg", "-r", *args], capture_output=True, text=True, timeout=1.0)
    except (subprocess.SubprocessError, OSError):
        return None


def walk(node, floating=False, workspace_rect=None):
    current_floating = floating or node.get("type") == "floating_con"
    if node.get("type") == "workspace":
        workspace_rect = node.get("rect") or workspace_rect
    children = node.get("nodes", []) or []
    floating_children = node.get("floating_nodes", []) or []
    if node.get("focused") and node.get("type") == "con" and not children and not floating_children:
        return node, current_floating, workspace_rect
    for child in children:
        found = walk(child, current_floating, workspace_rect)
        if found:
            return found
    for child in floating_children:
        found = walk(child, True, workspace_rect)
        if found:
            return found
    return None


def snap(con_id, width, height, x, y):
    r1 = sway(f"[con_id={con_id}]", "resize", "set", "width", str(width), "ppt", "height", str(height), "ppt")
    r2 = sway(f"[con_id={con_id}]", "move", "position", str(x), "ppt", str(y), "ppt")
    return bool(r1 and r2 and r1.returncode == 0 and r2.returncode == 0)


def main():
    if not os.environ.get("SWAYSOCK"):
        return
    print("Sway edge snapping active", flush=True)
    previous = {}
    last_snap = {}
    while True:
        try:
            result = sway("-t", "get_tree")
            if not result or result.returncode != 0:
                time.sleep(0.5)
                continue
            tree = json.loads(result.stdout)
            focused = walk(tree)
            now = time.monotonic()
            if not focused:
                time.sleep(POLL)
                continue
            node, is_floating, workrect = focused
            cid = node.get("id")
            rect = node.get("rect") or {}
            if not is_floating or cid is None or not all(k in rect for k in ("x", "y", "width", "height")) or not workrect:
                time.sleep(POLL)
                continue
            x, y = int(rect["x"]), int(rect["y"])
            w, h = int(rect["width"]), int(rect["height"])
            old = previous.get(cid)
            previous[cid] = (x, y, w, h)
            if old is None or now - last_snap.get(cid, 0) < COOLDOWN:
                time.sleep(POLL)
                continue
            moved = abs(x - old[0]) + abs(y - old[1]) >= 3
            same_size = abs(w - old[2]) <= 2 and abs(h - old[3]) <= 2
            if not moved or not same_size:
                time.sleep(POLL)
                continue
            wx, wy = int(workrect["x"]), int(workrect["y"])
            ww, wh = int(workrect["width"]), int(workrect["height"])
            left = x <= wx + EDGE
            right = x + w >= wx + ww - EDGE
            top = y <= wy + EDGE
            bottom = y + h >= wy + wh - EDGE
            target = None
            if top and left:
                target = (50, 50, 0, 0)
            elif top and right:
                target = (50, 50, 50, 0)
            elif bottom and left:
                target = (50, 50, 0, 50)
            elif bottom and right:
                target = (50, 50, 50, 50)
            elif left:
                target = (50, 100, 0, 0)
            elif right:
                target = (50, 100, 50, 0)
            elif top:
                target = (100, 100, 0, 0)
            if target:
                if snap(cid, *target):
                    last_snap[cid] = time.monotonic()
                    print(f"Snapped con_id={cid} to {target}", flush=True)
            time.sleep(POLL)
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            time.sleep(0.25)
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    main()
