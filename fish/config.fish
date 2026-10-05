# PATH (fish_add_path skips dirs that don't exist)
fish_add_path $HOME/.local/bin
fish_add_path /Library/TeX/texbin
fish_add_path $HOME/.bun/bin
fish_add_path $HOME/Library/pnpm
fish_add_path "$HOME/Library/Application Support/Herd/bin"
fish_add_path $HOME/.config/herd-lite/bin
fish_add_path $HOME/.opencode/bin
fish_add_path $HOME/.fabric/bin
fish_add_path $HOME/.hutch/bin
fish_add_path --append $HOME/.lmstudio/bin
fish_add_path --append $HOME/go/bin

set -gx BUN_INSTALL $HOME/.bun
set -gx PNPM_HOME $HOME/Library/pnpm
set -gx PHP_INI_SCAN_DIR $HOME/.config/herd-lite/bin $PHP_INI_SCAN_DIR
set -gx HERD_PHP_84_INI_SCAN_DIR "$HOME/Library/Application Support/Herd/config/php/84/"

# nnn
set -gx EDITOR code
set -gx NNN_SEL /tmp/.sel
set -gx NNN_PLUG 'p:preview-tui;c:cpfile;o:fzopen'
set -gx NNN_COLORS 4321
set -gx NNN_FCOLORS c1e2272e006033f7c6d6abc4

if status is-interactive
    set -g fish_greeting
    fish_config theme choose catppuccin-mocha
    set -g fish_color_command a6e3a1 # catppuccin green

    alias code="open -a 'Visual Studio Code'"
    alias lock="osascript -e 'tell application \"System Events\" to keystroke \"q\" using {control down, command down}'"
    alias tm=tmux
    function ls --description "nushell-style listing"
        set -l target (test (count $argv) -gt 0; and echo $argv[1]; or echo .)
        LS_PATH=$target nu -c 'ls ($env.LS_PATH | into glob) | sort-by type name'
    end
    function ll --description "nushell-style table listing"
        set -l target (test (count $argv) -gt 0; and echo $argv[1]; or echo .)
        LL_PATH=$target nu -c 'ls -a ($env.LL_PATH | into glob) | sort-by type name'
    end
    function lt --description "nushell-style tree table: lt [path] [depth]"
        nu ~/.config/fish/lt.nu $argv
    end
    alias cat=bat
    alias tyc="typst compile"
    alias gt="git status"
    alias cd=z
    alias qtserve="npx quartz build --serve"
    alias zr="hx ~/.config/fish/config.fish"
    alias zh="source ~/.config/fish/config.fish"
    alias ports="lsof -i -P -n | grep LISTEN | awk '{print \$1, \$2, \$9}' | column -t"
    alias claude="claude --dangerously-skip-permissions"
    alias hr=herdr
    alias sail=./vendor/bin/sail
    command -q kitty; and alias ssh="kitty +kitten ssh"

    starship init fish | source
    zoxide init fish | source
end
