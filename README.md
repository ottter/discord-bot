# Discord Bot

*Remastered* version of my original Discord bot, dodo. I might change the name of this if it gets to a point where I'm happy with it.

## How to run locally (Linux)

    cd ~
    git clone https://github.com/ottter/discord-bot.git && cd "$(basename "$_" .git)"
    python3 -m venv .venv               # Create virtual environment with a title in .gitignore
    source .venv/bin/activate           # Activate virtual environment
    pip install -r requirements.txt     # Install dependencies (including discord.py)
    ./main.py                           # Or just use an IDE...

## How to run on Heroku

todo

## Explanation of Parts

**config.py** - Contains private environment or global vars. In Linux you can have `~/.envar` with the below and run `source $HOME/.envar` and ideally add it to your `.bashrc`

    DISCORD_TOKEN={token}
    MONGO_TOKEN={token}

**Procfile** - Sync with Heroku. `gabe.py` is the main "chatbot" file that launches the modules

    worker: python3 gabe.py

**runtime.txt** - Heroku will automatically assign a Python runtime if not specified. Adding this is optional and locks the instance at that version

    python-3.9.5

**requirements.txt** - Helpful Python file to install all dependencies via:

    pip install -r requirements.txt

## Notes

Pre-maturity version (prior to removing anti-mod abuse features that are no longer required):

    git clone -b v0.9.0 https://github.com/ottter/gabe.git
