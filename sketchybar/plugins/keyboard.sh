#!/bin/bash

LAYOUT=$(defaults read ~/Library/Preferences/com.apple.HIToolbox.plist AppleSelectedInputSources \
  | grep -m1 '"KeyboardLayout Name"' | sed -E 's/.*= "?([^";]*)"?;/\1/')

sketchybar --set "$NAME" label="${LAYOUT:-?}"
