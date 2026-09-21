#!/bin/bash
# Claude Code statusline (aihero.dev style): repo | branch | S | U | A | context %
# Reads the statusline JSON Claude Code pipes to stdin.

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd')
pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
pct=$(printf '%.1f' "$pct")

if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  # Repo path relative to ~/dev/
  repo_name=$(echo "$cwd" | sed "s|^$HOME/dev/||")

  branch=$(git -C "$cwd" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)
  staged=$(git -C "$cwd" --no-optional-locks diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
  unstaged=$(git -C "$cwd" --no-optional-locks diff --name-only 2>/dev/null | wc -l | tr -d ' ')
  untracked=$(git -C "$cwd" --no-optional-locks ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')

  printf '\033[01;36m%s\033[00m | \033[01;32m%s\033[00m | S: \033[01;33m%s\033[00m | U: \033[01;33m%s\033[00m | A: \033[01;33m%s\033[00m | \033[01;33m%s%%\033[00m' \
    "$repo_name" "$branch" "$staged" "$unstaged" "$untracked" "$pct"
else
  printf '\033[01;36m%s\033[00m | \033[01;33m%s%%\033[00m' "$cwd" "$pct"
fi
