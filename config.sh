
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
alias tm="tmux"
alias ls="eza -lah"
alias lt="eza --tree --level=2 --long --git"
alias cat="bat"


. "$HOME/.local/bin/env"
. "$HOME/.deno/env"


export PATH="$PATH:$HOME/.lmstudio/bin"

