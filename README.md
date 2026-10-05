# dotfiles

This repo **is** `~/.config`. Clone it there; tools pick their config up from their usual paths.

## New machine setup

1. Back up anything already in `~/.config`, then clone:
   ```sh
   mv ~/.config ~/.config.old 2>/dev/null
   git clone git@github.com:ThomasLucking/.dotfiles.git ~/.config
   ```
2. Point Claude Code at its config:
   ```sh
   ln -s ~/.config/claude ~/.claude
   touch ~/.claude/.i-have-adhd-always
   ```
3. Copy `~/.agents/skills` from the old machine. 31 skills in `claude/skills/` are symlinks into it and stay broken without it.
4. Start `claude` and install the plugins in `claude/settings.json` → `enabledPlugins` (`/plugin` if not prompted).

## Gotchas

- `claude/settings.json` hardcodes `/Users/thomaslucking/` for the herdr hook. Different username = edit that path.
- Not tracked here: `~/.zshrc`, `~/.gitconfig`, `~/.ssh`, Homebrew packages. Copy them separately.
- `claude/` tracks config only (`CLAUDE.md`, `settings.json`, statusline, hooks, skills). Sessions, history and caches are gitignored.
- Credentials (`context7/`) are gitignored. Log in again (`npx ctx7@latest login`).
