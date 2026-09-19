# Discord Bot

*Remastered* version of my original Discord bot, dodo. I might change the name of this if it gets to a point where I'm happy with it.

-----------------------

## How to run locally (no venv)

    git clone https://github.com/ottter/discord-bot.git && cd "$(basename "$_" .git)"
    cp config.example.yaml config.yaml      # Fill in your token and settings
    python3 -m pip install --user -r requirements.txt
    python3 main.py

-----------------------

## How to run locally (Linux)

    git clone https://github.com/ottter/discord-bot.git && cd "$(basename "$_" .git)"
    cp config.example.yaml config.yaml      # Fill in your token and settings
    python3 -m venv .venv                   # Create virtual environment
    source .venv/bin/activate               # Activate virtual environment
    pip install -r requirements.txt         # Install dependencies
    tmux                                    # Optional: keeps the process alive over SSH
    python main.py
    ---
    tmux attach                             # Reconnect after reestablishing SSH connection
    [Ctrl+b] + [x]                          # Kill tmux session
    deactivate                              # Exit venv

-----------------------

## Configuration

Settings come from `config.yaml`, the environment, or both. The environment wins, and
the file is optional — with the token set, the bot runs without one.

| Variable | Default | Description |
| --- | --- | --- |
| `DISCORD_TOKEN` | — | **Required. Secret.** From the Discord Developer Portal. |
| `DISCORD_BOT_PRIMARY_ACCOUNT_PREFIX` | `,` | Prefix for text commands. |
| `LOG_FILE` | `discord.log` | Set to `""` to log only to stdout. The image does this. |

Any `DISCORD_BOT_*` variable becomes a config key with the prefix stripped, so
`DISCORD_BOT_WELCOME_CHANNEL` sets `WELCOME_CHANNEL`. Settings added later work the same
way, with no code or image change. `DISCORD_TOKEN` is also accepted bare, for secrets
injected by name.

Values are read as YAML, so `=123` is an int, `=true` a bool, `=["a","b"]` a list. The
token and command prefixes stay literal, so a prefix of `!` or `no` is the string you
wrote.

Enable the **Server Members** and **Message Content** intents in the Developer Portal,
or startup fails.

-----------------------

## Docker

Published to GHCR at `ghcr.io/ottter/discord-bot`. The image holds no config or secrets.

### Run the container

Use a file rather than `-e DISCORD_TOKEN=...`, which leaks into your shell history and
`docker inspect`:

    echo 'DISCORD_TOKEN=your-token-here' > bot.env && chmod 600 bot.env
    docker run -d --name discord-bot --restart unless-stopped \
      --env-file bot.env ghcr.io/ottter/discord-bot:latest

Add any other settings to the same file:

    DISCORD_BOT_PRIMARY_ACCOUNT_PREFIX=!

Or mount a `config.yaml` instead, if you prefer a file:

    docker run -d --name discord-bot --restart unless-stopped \
      -v /path/to/config.yaml:/app/config.yaml:ro ghcr.io/ottter/discord-bot:latest

### Update a running container

    docker pull ghcr.io/ottter/discord-bot:latest && \
    docker stop discord-bot && docker rm discord-bot && \
    docker run -d --name discord-bot --restart unless-stopped \
      --env-file bot.env ghcr.io/ottter/discord-bot:latest

### Pulling a private image

Only if the package is private. A pull credential needs `read:packages` and nothing
else; piping from `read` keeps it out of your shell history:

    read -rs GHCR_PAT && echo "$GHCR_PAT" | docker login ghcr.io -u USERNAME --password-stdin
    unset GHCR_PAT

### Build and push a new image

Actions does this on every push to main, and on `v*` tags — see
[docs/WORKFLOWS.md](docs/WORKFLOWS.md). By hand needs `write:packages` too:

    docker build -t ghcr.io/ottter/discord-bot:latest .
    docker push ghcr.io/ottter/discord-bot:latest

### Useful commands

    docker logs -f discord-bot          # Stream logs
    docker exec -it discord-bot sh      # Shell into running container (no bash in slim)
    docker ps                           # Check container status

-----------------------

## Notes

Pre-maturity version (prior to removing anti-mod abuse features that are no longer required):

    git clone -b v0.9.0 https://github.com/ottter/gabe.git
