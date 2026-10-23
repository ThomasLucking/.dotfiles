#!/bin/bash
source "$HOME/.config/sketchybar/colors.sh"

if ifconfig en0 | grep -q 'status: active'; then
  sketchybar --set "$NAME" icon=󰖩 icon.color=$BLUE
else
  sketchybar --set "$NAME" icon=󰖪 icon.color=$RED
fi
