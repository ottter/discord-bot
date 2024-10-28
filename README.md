# Discord Bot

*Remastered* version of my original Discord bot, dodo. I might change the name of this if it gets to a point where I'm happy with it.

-----------------------

## How to run locally (Linux)

    git clone https://github.com/ottter/discord-bot.git && cd "$(basename "$_" .git)"
    python3 -m venv .venv               # Create virtual environment with a title in .gitignore
    source .venv/bin/activate           # Activate virtual environment
    pip install -r requirements.txt     # Install dependencies (including discord.py)
    tmux                                # Optional; If connecting via SSH and you want to close connection
    python main.py                      # 
    ---
    tmux attach                         # Reconnect to tmux after reestablishing SSH connection
    [Ctrl+b] + [x]                      # Press while in tmux to kill session
    deactivate                          # Exit venv

## How to run via Docker

    sudo apt install docker.io
    # Create a PAT with  `write:packages`, `read:packages`, and `delete:packages`
    export GHCR_PAT="{TOKEN}"
    echo $GHCR_PAT | docker login ghcr.io -u ottter --password-stdin
    docker build -t ghcr.io/ottter/discord-bot:latest .
    docker push ghcr.io/ottter/discord-bot:latest

-----------------------

### Github Actions

GitHub Actions utilized in this project:

- [Pylint](https://pypi.org/project/pylint/)
- [GitHub Actions Status Embed for Discord](https://github.com/marketplace/actions/github-actions-status-embed-for-discord)
- [CodeQL Analysis](https://github.com/github/codeql-action)

**Pylint** - Static code analysis

    # run locally
    pylint --rcfile ./.pylintrc $(git ls-files '*.py')

    # run locally without adding pylint to PATH
    python -m pylint --rcfile ./.pylintrc $(git ls-files '*.py')

    # Or generate default pylint config file:
    pylint --generate-rcfile > ./.pylintrc

**Discord Status Embed** - Post in specified Discord channel a build's status. `DISCORD_WEBHOOK_TOKEN` and `GITHUB_TOKEN` are managed by Github.

**CodeQL Analysis** - Semantic code analysis engine

-----------------------

## Notes

Pre-maturity version (prior to removing anti-mod abuse features that are no longer required):

    git clone -b v0.9.0 https://github.com/ottter/gabe.git
