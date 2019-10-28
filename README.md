# ghistintime

```bash
# For bashrc.sh or bash_profile.sh
export PROMPT_COMMAND='python3.7 /path/to/ghist.py --database $HOME/.ghist.db put "$(fc -ln -0)"'

alias gh="python3.7 /path/to/ghist.py --database $HOME/.ghist.db get"
```

