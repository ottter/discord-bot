"""
Remastered version of my original Discord bot, which I used to "learn" Python
Entry point: loads config, sets up logging, and starts the bot
See ./README.md for setup and configuration
"""
import asyncio
import logging
import logging.handlers
import os
import sys
from pathlib import Path

import discord
import yaml
from discord.ext import commands

CONFIG_FILE = Path(__file__).parent / 'config.yaml'
REQUIRED_KEYS = ('DISCORD_TOKEN', 'PRIMARY_ACCOUNT_PREFIX')
DEFAULT_PREFIX = ','

# DISCORD_BOT_WELCOME_CHANNEL sets WELCOME_CHANNEL, so new settings need no code.
ENV_PREFIX = 'DISCORD_BOT_'
ENV_ALIASES = ('DISCORD_TOKEN',)   # also read bare, for injected secrets

# '!' and 'no' are valid YAML that parses to something else entirely.
VERBATIM_KEYS = frozenset({'DISCORD_TOKEN', 'PRIMARY_ACCOUNT_PREFIX', 'DEV_ACCOUNT_PREFIX'})

EXTENSION_DIRS = ('commands', 'listeners', 'slashes')
EXTENSION_EXCLUSIONS = ('help',)

log = logging.getLogger('discord.bot')


def config_from_env(environ) -> dict:
    """Pull config out of DISCORD_BOT_* variables and the bare aliases."""
    def value(key, raw):
        if key in VERBATIM_KEYS:
            return raw
        try:
            parsed = yaml.safe_load(raw)
        except yaml.YAMLError:
            return raw
        # YAML reads a bare '!' as empty, so keep the original.
        return raw if parsed is None and raw.strip() else parsed

    found = {}
    for name, raw in environ.items():
        key = name[len(ENV_PREFIX):] if name.startswith(ENV_PREFIX) else None
        if key:
            found[key] = value(key, raw)
    for name in ENV_ALIASES:
        if name in environ and name not in found:
            found[name] = value(name, environ[name])
    return found


def load_config() -> dict:
    """Read config.yaml, then let the environment override it.

    Either source alone works, so a container can run on env vars with no file.
    """
    config = {}
    if CONFIG_FILE.is_file():
        try:
            config = yaml.safe_load(CONFIG_FILE.read_text(encoding='utf-8')) or {}
        except yaml.YAMLError as err:
            sys.exit(f"Could not parse {CONFIG_FILE.name}: {err}\n")
        if not isinstance(config, dict):
            sys.exit(f"{CONFIG_FILE.name} must contain a mapping of keys to values.\n")

    config.update(config_from_env(os.environ))
    config.setdefault('PRIMARY_ACCOUNT_PREFIX', DEFAULT_PREFIX)

    missing = [k for k in REQUIRED_KEYS if not config.get(k)]
    if missing:
        sys.exit(f"Missing required config: {', '.join(missing)}\n"
                 f"Set them as {ENV_PREFIX}* environment variables, or copy "
                 "config.example.yaml to config.yaml and fill them in.\n")
    return config


def setup_logging():
    """Log to stdout, and to a rotating file unless LOG_FILE is empty."""
    logger = logging.getLogger('discord')
    # discord.py adds a NullHandler on import, which doesn't count.
    if any(not isinstance(h, logging.NullHandler) for h in logger.handlers):
        return
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{')

    def add(handler):
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Containers log to stdout and may have a read-only filesystem.
    log_file = os.environ.get('LOG_FILE', str(Path(__file__).parent / 'discord.log'))
    if log_file:
        try:
            add(logging.handlers.RotatingFileHandler(
                log_file, encoding='utf-8', maxBytes=32 * 1024 * 1024, backupCount=5))
        except OSError as err:
            print(f'File logging disabled ({log_file}): {err}', file=sys.stderr)

    if hasattr(sys.stdout, 'reconfigure'):  # Windows consoles default to cp1252
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    add(logging.StreamHandler(sys.stdout))


class DiscordBot(commands.Bot):
    """Loads extensions in setup_hook, the way discord.py 2.x wants it."""

    async def setup_hook(self) -> None:
        """Runs after login, before the gateway connects."""
        await self.load_extensions()

    async def load_extensions(self) -> None:
        """Load every module under modules/, minus the exclusions."""
        loaded, failed = [], []

        for dir_ in EXTENSION_DIRS:
            dir_path = Path(__file__).parent / 'modules' / dir_
            if not dir_path.is_dir():
                continue

            for file in sorted(dir_path.glob('*.py')):
                if file.stem in EXTENSION_EXCLUSIONS:
                    continue
                try:
                    await self.load_extension(f'modules.{dir_}.{file.stem}')
                    loaded.append(file.stem)
                except commands.ExtensionError as err:
                    cause = getattr(err, 'original', err)
                    failed.append(file.stem)
                    log.error('Could not load %s: %s: %s',
                              file.stem, type(cause).__name__, cause)

        log.info('Loaded %s extension(s): %s', len(loaded), ', '.join(loaded) or 'none')
        if failed:
            log.warning('Failed to load: %s', ', '.join(failed))


async def main():
    """Set up logging, build the bot, run until it disconnects."""
    setup_logging()

    config = load_config()
    token = config["DISCORD_TOKEN"]
    prefix = config["PRIMARY_ACCOUNT_PREFIX"]

    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    # The context manager closes the HTTP session and gateway on the way out.
    async with DiscordBot(command_prefix=prefix, intents=intents, help_command=None) as bot:
        log.info('Starting up ...')
        try:
            await bot.start(token)
        except discord.LoginFailure as error:
            log.critical('Discord login failed: %s', error)
            sys.exit("Login Unsuccessful\n")
        except discord.PrivilegedIntentsRequired as error:
            log.critical('Privileged intents are off in the Developer Portal: %s', error)
            sys.exit("Enable the Members and Message Content intents for this bot\n")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info('Shutting down.')
