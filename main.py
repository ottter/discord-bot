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

EXTENSION_EXCLUSIONS = ('help',)

log = logging.getLogger('discord.bot')


def find_extensions() -> list:
    """Every loadable extension under modules/, as dotted import paths.

    A package (directory with __init__.py) loads as one extension, so a feature
    can split itself across files and still register from one setup(). Loose
    .py files in a subdirectory each load on their own.
    """
    root = Path(__file__).parent / 'modules'
    found = []

    for path in sorted(root.iterdir()):
        if path.name.startswith(('_', '.')) or path.stem in EXTENSION_EXCLUSIONS:
            continue

        if path.is_dir():
            if (path / '__init__.py').is_file():
                found.append(f'modules.{path.name}')
                continue
            found += [f'modules.{path.name}.{file.stem}'
                      for file in sorted(path.glob('*.py'))
                      if not file.stem.startswith('_')
                      and file.stem not in EXTENSION_EXCLUSIONS]

    return found


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

    from_env = config_from_env(os.environ)
    config.update(from_env)
    config.setdefault('PRIMARY_ACCOUNT_PREFIX', DEFAULT_PREFIX)

    sources = []
    if CONFIG_FILE.is_file():
        sources.append(CONFIG_FILE.name)
    if from_env:
        sources.append(f'{len(from_env)} environment variable(s)')
    log.info('Config loaded from %s', ' and '.join(sources) or 'nothing')

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
    # LOG_LEVEL only turns up our own logging; discord.py at DEBUG dumps every
    # HTTP payload. A typo shouldn't stop the bot booting, so fall back to INFO.
    level = os.environ.get('LOG_LEVEL', '').upper() or 'INFO'
    try:
        logging.getLogger('discord.bot').setLevel(level)
    except ValueError:
        print(f'Unknown LOG_LEVEL {level!r}, using INFO', file=sys.stderr)
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

    def __init__(self, *args, config=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Cogs read their settings off this rather than the environment.
        self.config = config or {}

    async def setup_hook(self) -> None:
        """Runs after login, before the gateway connects."""
        await self.load_extensions()

    async def load_extensions(self) -> None:
        """Load every extension under modules/, minus the exclusions."""
        loaded, failed = [], []

        for name in find_extensions():
            try:
                await self.load_extension(name)
                loaded.append(name.rsplit('.', 1)[-1])
            except commands.ExtensionError as err:
                cause = getattr(err, 'original', err)
                failed.append(name.rsplit('.', 1)[-1])
                log.error('Could not load %s: %s: %s',
                          name, type(cause).__name__, cause)

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
    async with DiscordBot(command_prefix=prefix, intents=intents, help_command=None,
                          config=config) as bot:
        log.info('Starting up version %s ...', os.environ.get('BOT_VERSION') or 'dev')
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
