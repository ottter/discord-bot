# Discord Bot

*Remastered* version of my original Discord bot, dodo. I might change the name of this if it gets to a point where I'm happy with it.

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

## Docker

The bot is packaged as a Docker image and published to the GitHub Container Registry (GHCR) at
`ghcr.io/ottter/discord-bot`.

### First-time setup

Install Docker and log in to GHCR with a Personal Access Token (PAT) scoped to
`read:packages`, `write:packages`, and `delete:packages`:

    sudo apt install docker.io
    export GHCR_PAT="{TOKEN}"
    echo $GHCR_PAT | docker login ghcr.io -u ottter --password-stdin

### Build and push a new image

    docker build -t ghcr.io/ottter/discord-bot:latest .
    docker push ghcr.io/ottter/discord-bot:latest

### Run the container

`config.yaml` is bind-mounted at runtime so the token never bakes into the image:

    docker run -d --name discord-bot --restart unless-stopped \
      -v /path/to/config.yaml:/app/config.yaml:ro ghcr.io/ottter/discord-bot:latest

### Update a running container

Pull the latest image and recreate the container:

    docker pull ghcr.io/ottter/discord-bot:latest
    docker stop discord-bot
    docker rm discord-bot
    docker run -d --name discord-bot --restart unless-stopped \
      -v /path/to/config.yaml:/app/config.yaml:ro ghcr.io/ottter/discord-bot:latest

Or as a one-liner if the run flags haven't changed:

    docker pull ghcr.io/ottter/discord-bot:latest && \
    docker stop discord-bot && docker rm discord-bot && \
    docker run -d --name discord-bot --restart unless-stopped \
      -v /path/to/config.yaml:/app/config.yaml:ro ghcr.io/ottter/discord-bot:latest

### Useful commands

    docker logs -f discord-bot          # Stream logs
    docker exec -it discord-bot bash    # Shell into running container
    docker ps                           # Check container status

-----------------------

### Github Actions

GitHub Actions utilized in this project:

- [Pylint](https://pypi.org/project/pylint/)
- [CodeQL Analysis](https://github.com/github/codeql-action)

**Pylint** - Static code analysis

    # run locally
    pylint --rcfile ./.pylintrc $(git ls-files '*.py')

    # run locally without adding pylint to PATH
    python -m pylint --rcfile ./.pylintrc $(git ls-files '*.py')

    # Or generate default pylint config file:
    pylint --generate-rcfile > ./.pylintrc

**CodeQL Analysis** - Semantic code analysis engine

-----------------------

## Notes

Pre-maturity version (prior to removing anti-mod abuse features that are no longer required):

    git clone -b v0.9.0 https://github.com/ottter/gabe.git
