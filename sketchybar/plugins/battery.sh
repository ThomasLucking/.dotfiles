#!/bin/bash
source "$HOME/.config/sketchybar/colors.sh"

INFO="$(pmset -g batt)"
PCT=$(echo "$INFO" | grep -Eo '[0-9]+%' | tr -d '%')
[ -z "$PCT" ] && exit 0

case $PCT in
  9[0-9]|100) ICON=󰁹 COLOR=$GREEN ;;
  [6-8][0-9]) ICON=󰂀 COLOR=$GREEN ;;
  [3-5][0-9]) ICON=󰁾 COLOR=$YELLOW ;;
  [1-2][0-9]) ICON=󰁼 COLOR=$PEACH ;;
  *)          ICON=󰁺 COLOR=$RED ;;
esac
echo "$INFO" | grep -q 'AC Power' && ICON=󰂄

sketchybar --set "$NAME" icon="$ICON" icon.color=$COLOR label="$PCT%"
