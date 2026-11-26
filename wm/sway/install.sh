#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
    echo "Run this script with: bash install.sh"
    return 1
fi

if [[ "${EUID}" -eq 0 ]]; then
    echo "Run as your normal user, without sudo."
    exit 1
fi

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$HOME/.config"
BACKUP="$CONFIG/sway-backups/$(date +%Y%m%d-%H%M%S)"

if command -v sudo >/dev/null 2>&1; then
    SUDO=(sudo)
elif command -v doas >/dev/null 2>&1; then
    SUDO=(doas)
else
    SUDO=()
fi

need_admin() {
    if [[ ${#SUDO[@]} -eq 0 ]]; then
        echo "Package installation needs sudo or doas."
        return 1
    fi
}

install_packages() {
    if command -v pacman >/dev/null 2>&1; then
        if need_admin && "${SUDO[@]}" pacman -S --needed git base-devel waybar; then
            if command -v yay >/dev/null 2>&1; then
                if yay -S --needed swayfx waybar; then return 0; fi
            elif command -v paru >/dev/null 2>&1; then
                if paru -S --needed swayfx waybar; then return 0; fi
            else
                local tmp
                tmp="$(mktemp -d)"
                echo "Building SwayFX from the Arch User Repository..."
                if git clone https://aur.archlinux.org/swayfx.git "$tmp/swayfx" &&
                   (cd "$tmp/swayfx" && makepkg -si); then
                    rm -rf "$tmp"
                    return 0
                fi
                rm -rf "$tmp"
            fi
        fi
    elif command -v apt-get >/dev/null 2>&1; then
        if apt-cache show swayfx >/dev/null 2>&1 &&
           apt-cache show waybar >/dev/null 2>&1 && need_admin; then
            if "${SUDO[@]}" apt-get update &&
               "${SUDO[@]}" apt-get install -y swayfx waybar; then return 0; fi
        fi
    elif command -v dnf >/dev/null 2>&1; then
        if need_admin && "${SUDO[@]}" dnf install -y swayfx waybar; then return 0; fi
    elif command -v zypper >/dev/null 2>&1; then
        if need_admin && "${SUDO[@]}" zypper --non-interactive install swayfx waybar; then return 0; fi
    elif command -v apk >/dev/null 2>&1; then
        if need_admin && "${SUDO[@]}" apk add swayfx waybar; then return 0; fi
    elif command -v xbps-install >/dev/null 2>&1; then
        if need_admin && "${SUDO[@]}" xbps-install -S swayfx waybar; then return 0; fi
    fi

    # Try Nix even if the detected distribution's package-manager path failed.
    if command -v nix >/dev/null 2>&1; then
        echo "Trying Nix packages for SwayFX and Waybar..."
        if nix profile install github:wlrfx/swayfx nixpkgs#waybar; then return 0; fi
    fi

    echo
    echo "Could not automatically install both SwayFX and Waybar."
    echo "Your distro may need an extra repository or a different build method."
    echo "See https://github.com/wlrfx/swayfx for distro-specific instructions."
    return 1
}

install_packages || exit 1

mkdir -p "$BACKUP"
for item in sway waybar; do
    if [[ -e "$CONFIG/$item" ]]; then
        cp -a "$CONFIG/$item" "$BACKUP/$item"
    fi
done

mkdir -p "$CONFIG/sway" "$CONFIG/waybar"
install -m 0644 "$ROOT/config" "$CONFIG/sway/config"
install -m 0644 "$ROOT/waybar/config.jsonc" "$CONFIG/waybar/config.jsonc"
install -m 0644 "$ROOT/waybar/style.css" "$CONFIG/waybar/style.css"

if [[ -f "$ROOT/waybar/cal.sh" ]]; then
    install -m 0755 "$ROOT/waybar/cal.sh" "$CONFIG/waybar/cal.sh"
fi

# Install helper scripts into ~/.local/bin
mkdir -p "$HOME/.local/bin"
for helper in sway-swipe-ws sway-edge-snap.py swayshortcuts swaym; do
    if [[ -f "$ROOT/$helper" ]]; then
        install -m 0755 "$ROOT/$helper" "$HOME/.local/bin/$helper"
    else
        echo "WARN: helper not found, skipping: $helper" >&2
    fi
done

echo
echo "SwayFX and Waybar setup completed."
echo "Config backup: $BACKUP"
echo "Log out and choose SwayFX in your session selector."
echo "Review the Sway config for commands or paths specific to your machine."
