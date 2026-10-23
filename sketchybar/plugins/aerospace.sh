#!/bin/bash
source "$HOME/.config/sketchybar/colors.sh"

FOCUSED="${FOCUSED_WORKSPACE:-$(aerospace list-workspaces --focused)}"

if [ "$1" = "$FOCUSED" ]; then
  sketchybar --set "$NAME" background.color=$MAUVE icon.color=$BASE
else
  sketchybar --set "$NAME" background.color=$SURFACE0 icon.color=$TEXT
fi
