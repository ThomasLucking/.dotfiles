#!/usr/bin/env bash
# Claude Code statusline: model, context %, token count, cost — color-coded.
# Reads the statusline JSON Claude Code pipes to stdin.

input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name')
pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
in_tok=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
out_tok=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
total_tok=$((in_tok + out_tok))
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')

# Format token count as "24.5k" once over 1000, plain number otherwise
if [ "$total_tok" -ge 1000 ]; then
  tok_display=$(awk -v t="$total_tok" 'BEGIN { printf "%.1fk", t/1000 }')
else
  tok_display="$total_tok"
fi

# ANSI colors
RESET='\033[0m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[36m'
DIM='\033[2m'

# Context % color thresholds: green <50, yellow <80, red >=80
pct_int=${pct%.*}
if [ "$pct_int" -lt 50 ]; then
  pct_color=$GREEN
elif [ "$pct_int" -lt 80 ]; then
  pct_color=$YELLOW
else
  pct_color=$RED
fi

# Cost color thresholds: green <$1, yellow <$5, red >=$5
cost_int=$(printf '%.0f' "$cost")
if [ "$cost_int" -lt 1 ]; then
  cost_color=$GREEN
elif [ "$cost_int" -lt 5 ]; then
  cost_color=$YELLOW
else
  cost_color=$RED
fi

printf "${CYAN}[%s]${RESET} ${pct_color}%s%%${RESET} ${DIM}context${RESET} ${DIM}(%s tok)${RESET} ${cost_color}\$%.2f${RESET}\n" \
  "$model" "$pct" "$tok_display" "$cost"
