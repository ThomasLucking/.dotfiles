#!/bin/bash

CORES=$(sysctl -n hw.ncpu)
CPU=$(ps -A -o %cpu= | awk -v c="$CORES" '{s+=$1} END {printf "%d", s/c}')
# Activity Monitor "Memory Used" (same formula as the Stats app)
RAM=$(vm_stat | awk -F'[:.]' '/page size/ {split($0,a," "); ps=a[8]} {gsub(/ /,"",$2); v[$1]=$2}
  END {u = v["Pages active"] + v["Pages inactive"] + v["Pages speculative"] + v["Pages wired down"] \
         + v["Pages occupied by compressor"] - v["Pages purgeable"] - v["File-backed pages"];
       printf "%.1fG", u*ps/1073741824}')

sketchybar --set cpu label="${CPU}%" \
           --set ram label="${RAM}"
