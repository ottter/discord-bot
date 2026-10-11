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
| `LOG_LEVEL` | `INFO` | Set to `DEBUG` for verbose bot logging while testing. |
| `DISCORD_BOT_KRILLION_DB` | `data/krillion.db` | SQLite file for Krillion scores. Mount a volume here to keep them across restarts. |
| `DISCORD_BOT_KRILLION_SUBMIT_CHANNEL` | unset | Channel id where scores count. Unset means any channel. |
| `DISCORD_BOT_KRILLION_COOLDOWN` | `60` | Seconds between stored scores, per user. |
| `DISCORD_BOT_WORDLE_DB` | `data/wordle.db` | SQLite file for Wordle answers, boards and results. Mount a volume here too. |
| `DISCORD_BOT_WORDLE_BOARDS` | `3` | Boards a game needs before the bot plays and locks in its result. |
| `DISCORD_BOT_WORDLE_APP_ID` | `1211781489931452447` | The Wordle app's account, whose posts are read. |
| `DISCORD_BOT_WORDLE_TZ` | `America/New_York` | Timezone for today's game number when no image has shown a newer one. |

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

## Layout

    main.py                  entry point: config, logging, startup
    modules/
      base/                  small always-on cogs (on_ready, test commands)
      krillion/              the Krillion feature, loaded as one extension
      wordle/                the Wordle feature, loaded as one extension
        data/                word list, past answers, digit shapes
        tools/               tuning and rebuild scripts, not run by the bot

Anything under `modules/` loads automatically. A directory with an `__init__.py` loads
as a single extension, so a feature can spread across files and register from one
`setup()`; loose `.py` files in a subdirectory each load on their own.

-----------------------

## Krillion

Paste a [krillion.io](https://krillion.io) daily share into any channel and the bot
records it:

    Krillion #66 🦐
    300

    🦑🐟🐟🐟🦑🦑🐟

It reacts ✅ when a score is saved and ❌ with a reason when it won't count.
Re-submitting the same day quietly replaces your previous score.

Shares are read in every channel. Set `DISCORD_BOT_KRILLION_SUBMIT_CHANNEL` to a channel
id to make scores count only there — pasting elsewhere gets a reply pointing at the right
channel.

Only the current day counts — archive (⟲) and unlimited (∞) runs are rejected, as are
yesterday's shares after the midnight Eastern reset.

Each person can store one score a minute; the limit is per user, so everyone posting at
once is fine. Anything past that is ignored without comment. A rejected paste doesn't
count against the limit, so fixing a bad one is free.

Leaderboards are per server, with ties broken by who submitted first.

| Command | |
| --- | --- |
| `/krillion today` | Standings so far today |
| `/krillion results [day]` | Render a day's results on demand |
| `/krillion stats [member]` | Dives, average, best, streak |
| `/krillion channel [#channel]` | Where daily results post. Needs Manage Server |
| `/version` | Which build is running |

Running in Kubernetes? See [docs/kubernetes.md](docs/kubernetes.md) for the volume the
database needs.

Results post automatically just after the daily reset, but only once a server runs
`/krillion channel` — there is no default channel, so nothing posts until you set one.
Scores live in a SQLite file — see `DISCORD_BOT_KRILLION_DB` above. To start over,
delete that file and restart.

-----------------------

## Wordle

The bot plays each day's Wordle in hard mode, using only the colors on other people's
finished boards. It reads the Wordle app's posts and pools every server's boards for a
game. Once a server's own posts show three finished boards, the bot plays and posts its
result there like a share, colors only:

    Wordle 1,938 3/6*
    ⬛⬛🟨⬛⬛
    🟨⬛🟨🟩🟩
    🟩🟩🟩🟩🟩
    Played from 5 boards. Starting blind with slate, I'd have gotten 4/6.

That result is locked in for the day. A server that never reaches three is locked in
quietly once the game is over in every timezone. The bot never sees the answer before
playing; it's looked up once per game, from NYT, only to color the bot's own guesses.

| Command | |
| --- | --- |
| `/wordle play [game]` | Play today's game from the boards so far and post the result. The last one stands if the server never reaches three boards. With a game number, replays that game instead; nothing newer than the latest released game |
| `/wordle today` | The same with the guesses and answer in spoilers, only for you |
| `/wordle simulate word` | Watch it play any word, with no boards |
| `/wordle channel [#channel]` | Where locked-in results post. Unset means next to the app's message. Needs Manage Server |

The commands work without the Wordle app; today's game comes from the date in
`DISCORD_BOT_WORDLE_TZ`. Answers, boards and results live in `DISCORD_BOT_WORDLE_DB`,
which wants the same volume as Krillion's. On startup the bot spends about a minute
building tables for reading boards, in the background, and holds about 35 MB for them.

How it plays, and how it was tuned, is in [modules/wordle/README.md](modules/wordle/README.md).

-----------------------

## Notes

Pre-maturity version (prior to removing anti-mod abuse features that are no longer required):

    git clone -b v0.9.0 https://github.com/ottter/gabe.git
