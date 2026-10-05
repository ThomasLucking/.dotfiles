#!/bin/sh
# Hyprland-style dwindle for AeroSpace.
# Called from on-window-detected: AEROSPACE_WINDOW_ID is the new window, which
# AeroSpace has inserted right after the previously focused window. Joining it
# with that window nests the pair in a container of opposite orientation, so
# every new window splits the focused one instead of squeezing into one row.

aerospace=/opt/homebrew/bin/aerospace
id=$AEROSPACE_WINDOW_ID
[ -n "$id" ] || exit 0

info=$($aerospace list-windows --all --format '%{window-id} %{workspace} %{window-layout}' |
    awk -v id="$id" '$1 == id { print $2, $3 }')
workspace=${info% *}
layout=${info#* }

# First split on a workspace stays side by side
tiled=$($aerospace list-windows --workspace "$workspace" --format '%{window-layout}' |
    grep -vc floating)
[ "$tiled" -gt 2 ] || exit 0

case $layout in
    h_tiles) $aerospace join-with --window-id "$id" left ;;
    v_tiles) $aerospace join-with --window-id "$id" up ;;
esac
