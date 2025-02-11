# ghistintime

```bash
# install
pip install git+ssh://git@github.com/possemeeg/ghistintime.git@dev-upgrade

# For bashrc.sh or bash_profile.sh
export PROMPT_COMMAND=gh_put "$(fc -ln -0)"

```

## Config
- Config is stored in ~/.config/ghistintime/config.cfg
- Currently this is only the database.
- Database defaults to ~/.config/ghistintime/ghist.db
- Thus if no config is created, all that you'll get is `~/.config/ghistintime/ghist.db`.
- Thus (II) make sure your existing db is copied to `~/.config/ghistintime/ghist.db`.

