# Discord Bot

*Remastered* version of my original Discord bot, dodo. I might change the name of this if it gets to a point where I'm happy with it.

-----------------------

## How to run locally (Linux)

    cd ~
    git clone https://github.com/ottter/discord-bot.git && cd "$(basename "$_" .git)"
    python3 -m venv .venv               # Create virtual environment with a title in .gitignore
    source .venv/bin/activate           # Activate virtual environment
    pip install -r requirements.txt     # Install dependencies (including discord.py)
    ./main.py                           # Or just use an IDE...

## How to run via Heroku

Originally I had this deploy only to GitHub and then a pipeline to automatically deploy from there. Since the [breach](https://thehackernews.com/2022/04/github-notifies-victims-whose-private.html) with disabled GitHub authentication, I just use Heroku CLI to push out changes.

    heroku login
    (existing) heroku git:remote -a {app-name}     # Will require authorized app owner/developer
    (or clone) heroku git:clone -a {app-name}      # Which one depends if repo is on system already
    git push heroku main

## How to run via Docker

    # getting started
    git clone https://github.com/ottter/discord-bot.git && cd "$(basename "$_" .git)"
    docker build --tag discord-bot .    # Build the image from a Dockerfile
    docker run --detach discord-bot     # Run the container in background
    ---
    # docker container management
    docker ps -a                        # List ALL containers
    docker kill {container-id}          # kill select container
    docker rm {container-id}            # remove select container

    docker kill $(docker ps -q)         # Stop ALL containers
    docker rm $(docker ps -a -q)        # Remove ALL containers
    ---
    # docker image management
    docker image ls                     # List ALL images
    docker rmi {image-id}               # Remove select image
    
    docker rmi $(docker images -q)      # Remove ALL images

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
