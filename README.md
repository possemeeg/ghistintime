# ghistintime

```bash
# For bashrc.sh or bash_profile.sh
export PROMPT_COMMAND='python3.7 /path/to/ghist.py --database $HOME/.ghist.db put "$(fc -ln -0)"'

export GHIST_SCRIPT="$HOME/Development/scripts/ghist.py"
export GHIST_DB="$HOME/.ghist.db"

alias gh="python3.7 $GHIST_SCRIPT --database $GHIST_DB get"
alias gha="python3.7 $GHIST_SCRIPT --database $GHIST_DB ass"
alias ghr="python3.7 $GHIST_SCRIPT --database $GHIST_DB ref"
alias ghe="python3.7 $GHIST_SCRIPT --database $GHIST_DB ex"
```

