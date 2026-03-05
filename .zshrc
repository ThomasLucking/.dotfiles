
HISTFILE=$HOME/.zhistory
SAVEHIST=1000
HISTSIZE=999
setopt share_history
setopt hist_expire_dups_first
setopt hist_ignore_dups
setopt hist_verify


if [ -f /opt/homebrew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]; then
    source /opt/homebrew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
fi


alias code="open -a 'Visual Studio Code'"
alias lock="osascript -e 'tell application \"System Events\" to keystroke \"q\" using {control down, command down}'"
alias tm="tmux"
alias ls="eza"
alias ll="eza -lah"
alias lt="eza --tree --level=2 --long --git"
alias cat="bat"
alias tyc="typst compile"
alias gcommit="/Users/thomaslucking/Desktop/Automation/git.sh"
alias gt="git status"
alias cd="z"
alias qtserve="npx quartz build --serve"
alias zr="hx ~/.zshrc"


. "$HOME/.local/bin/env"
. "$HOME/.deno/env"


export PATH="$PATH:$HOME/.lmstudio/bin"
eval "$(starship init zsh)"


export PATH="/Users/thomaslucking/.config/herd-lite/bin:$PATH"
export PHP_INI_SCAN_DIR="/Users/thomaslucking/.config/herd-lite/bin:$PHP_INI_SCAN_DIR"

# bun completions
[ -s "/Users/thomaslucking/.bun/_bun" ] && source "/Users/thomaslucking/.bun/_bun"

# bun
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
export PATH="/Library/TeX/texbin:$PATH"

# pnpm
export PNPM_HOME="/Users/thomaslucking/Library/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac
# pnpm end


# Herd injected PHP 8.4 configuration.
export HERD_PHP_84_INI_SCAN_DIR="/Users/thomaslucking/Library/Application Support/Herd/config/php/84/"


# Herd injected PHP binary.
export PATH="/Users/thomaslucking/Library/Application Support/Herd/bin/":$PATH

# opencode
export PATH=/Users/thomaslucking/.opencode/bin:$PATH
export PATH=$JAVA_HOME/bin:$PATH
source $(brew --prefix)/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source $(brew --prefix)/share/zsh-autosuggestions/zsh-autosuggestions.zsh

eval "$(zoxide init zsh)
"export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion


 # nnn config
export EDITOR="code"  
export NNN_SEL='/tmp/.sel'
export NNN_PLUG='p:preview-tui;c:cpfile;o:fzopen'
export NNN_COLORS='4321'
export NNN_FCOLORS='c1e2272e006033f7c6d6abc4'
