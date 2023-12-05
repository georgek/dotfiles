# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# git prompt
if [[ -n $SSH_CLIENT ]]; then
    user_host_colour='1;33'     # yellow
else
    user_host_colour='1;32'     # green
fi

user_host='\[\e['$user_host_colour'm\]\u@\h'

wd='\[\e[1;34m\]\w'             # blue

if hash git 2>/dev/null; then
    source $HOME/.bash.d/git-prompt.sh
    export GIT_PS1_SHOWDIRTYSTATE=1
    git_prompt='\[\e[1;31m\]$(__git_ps1)\[\e[1;0;37m\]' # red
else
    git_prompt=''
fi

end='\$\[\e[00m\]'

if [ "$TERM" = "xterm" ]; then
    export TERM=xterm-256color
fi

# If this is an xterm set the title to user@host:dir
case "$TERM" in
    "dumb")
        PS1="> "
        ;;
    xterm*|rxvt*|eterm*|screen*)
        PS1="$user_host $wd$git_prompt $end "
        PS1="\[\e]0;\u@\h: \w\a\]$PS1"
        ;;
    *)
        ;;
esac

# helper function for emacs vterm
vterm_printf() {
    if [ -n "$TMUX" ] && ([ "${TERM%%-*}" = "tmux" ] || [ "${TERM%%-*}" = "screen" ]); then
        # Tell tmux to pass the escape sequences through
        printf "\ePtmux;\e\e]%s\007\e\\" "$1"
    elif [ "${TERM%%-*}" = "screen" ]; then
        # GNU screen (screen, screen-256color, screen-256color-bce)
        printf "\eP\e]%s\007\e\\" "$1"
    else
        printf "\e]%s\e\\" "$1"
    fi
}

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable color support of ls and also add handy aliases
if [ "$TERM" != "dumb" ]; then
    eval "`dircolors -b`"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
fi

# some more ls aliases
alias ll='ls -lh'
alias la='ls -A'
alias l='ls -CF'

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi

# sudo completion
complete -cf sudo

# these are scripts living in ~/bin
export ALTERNATE_EDITOR="" \
       EDITOR="editor" \
       SUDO_EDITOR="visual" \
       VISUAL="visual"

export PATH=$HOME/bin:$HOME/.local/bin:$PATH

### History Stuff

# allow use of C-s
stty -ixon

HISTFILESIZE=
HISTSIZE=
HISTTIMEFORMAT="[%F %T] "

# don't put duplicate lines in the history and ignore lines starting with space
export HISTCONTROL=ignoreboth

shopt -s histappend

# record local history when DIRENV_FILE and LOCAL_HISTFILE is set
_set_local_histfile() {
    history -a

    if [[ -n $DIRENV_FILE ]] && [[ -n $LOCAL_HISTFILE ]]; then
        local histfile_local=${HOME}/.bash_history.d/${DIRENV_FILE%\/*}
        mkdir -p $(dirname $histfile_local)
        touch $histfile_local
        chmod 600 $histfile_local
    else
        local histfile_local=${HOME}/.bash_history
    fi

    [[ "$HISTFILE" == "$histfile_local" ]] && return

    # switch history to new file
    echo "Writing Bash history to $histfile_local"

    history -w
    history -c

    export HISTFILE=$histfile_local

    history -r
}

PROMPT_COMMAND="_set_local_histfile;$PROMPT_COMMAND"

# direnv
if hash direnv 2>/dev/null; then
    eval "$(direnv hook bash)"
fi

# python venv
show_virtual_env() {
  if [[ -n "$VIRTUAL_ENV" && -n "$DIRENV_DIR" ]]; then
    echo "($(basename $VIRTUAL_ENV)) "
  fi
}
export -f show_virtual_env
PS1='$(show_virtual_env)'$PS1

# golang
if hash go 2>/dev/null; then
    unset GOPATH
    export PATH=$(go env GOPATH)/bin:$PATH
fi

# virtualenvwrapper
if hash virtualenvwrapper.sh 2>/dev/null; then
    export WORKON_HOME=$HOME/.virtualenvs
    export PROJECT_HOME=$HOME/code
    source virtualenvwrapper.sh
fi

# pyenv
# export PATH="/home/gk/.pyenv/bin:$PATH"
# eval "$(pyenv init -)"
#eval "$(pyenv virtualenv-init -)"
# pyenv virtualenvwrapper_lazy

# nvm
export NVM_DIR="$HOME/dotfiles/nvm/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# pipx
if hash pipx 2>/dev/null; then
    eval "$(register-python-argcomplete pipx)"
fi

# kubectl
if hash kubectl 2>/dev/null; then
    source <(kubectl completion bash)
    export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
fi
