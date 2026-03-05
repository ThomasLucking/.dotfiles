
#!/bin/bash

DEST=~/Desktop/Code/.dotfiles

# Shell & git
cp ~/.zshrc "$DEST/"
cp ~/.gitconfig "$DEST/"
cp -r ~/.ssh "$DEST/"

# Config dirs
mkdir -p "$DEST/.config"
for dir in gh nvim raycast btop git neofetch helix powershell uv opencode starship.toml nnn kitty zed; do
  sudo cp -r ~/.config/$dir "$DEST/.config/"
done

# Brew lists
brew list > "$DEST/brew-packages.txt"
brew list --cask > "$DEST/brew-casks.txt"

echo "✅ Done! Everything copied to $DEST"
