"""
Remastered version of my original Discord bot, which I used to "learn" Python
This is the main setup file that is used to run the entire bot
Reference ./README.md for instructions and useful information
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

REQUIRED_CONFIG_KEYS = {"DISCORD_TOKEN", "PRIMARY_ACCOUNT_PREFIX"}

DEFAULT_PREFIX = ','

# Any DISCORD_BOT_* variable becomes a config key with the prefix stripped, so
# DISCORD_BOT_WELCOME_CHANNEL sets WELCOME_CHANNEL. New settings need no change here.
ENV_PREFIX = 'DISCORD_BOT_'

# Aliases accepted without the prefix, for secrets wired up by name elsewhere
# (Kubernetes secretKeyRef, --env-file, CI). Kept deliberately short.
ENV_ALIASES = ('DISCORD_TOKEN',)

# Never YAML-parsed: a token is an opaque string, and a prefix like '!' or '>'
# is valid YAML syntax that would parse to something other than itself.
VERBATIM_KEYS = frozenset({
    'DISCORD_TOKEN', 'PRIMARY_ACCOUNT_PREFIX', 'DEV_ACCOUNT_PREFIX',
})

EXTENSION_DIRS = ('commands', 'listeners', 'slashes')
EXTENSION_EXCLUSIONS = ('help',)

log = logging.getLogger('discord.bot')


def parse_env_value(key: str, raw: str):
    """Coerce an environment string into the type config.yaml would have produced.

    Lists, numbers and booleans are written as YAML so they behave the same from
    either source. Keys in VERBATIM_KEYS, and anything YAML reads as empty, keep
    the original string — that is what saves a '!' prefix or a token from being
    reinterpreted.
    """
    if key in VERBATIM_KEYS:
        return raw
    try:
        parsed = yaml.safe_load(raw)
    except yaml.YAMLError:
        return raw
    return raw if parsed is None and raw.strip() else parsed


def config_from_env(environ) -> dict:
    """Collect config keys from DISCORD_BOT_* variables and the bare aliases."""
    found = {}
    for name, raw in environ.items():
        if name.startswith(ENV_PREFIX):
            key = name[len(ENV_PREFIX):]
            if key:
                found[key] = parse_env_value(key, raw)
    # Bare aliases lose to the prefixed form, which is unambiguous.
    for name in ENV_ALIASES:
        if name in environ and name not in found:
            found[name] = parse_env_value(name, environ[name])
    return found


def load_config() -> dict:
    """Build config from config.yaml and the environment.

    Either source alone is enough. Environment variables win over the file, so a
    container can supply DISCORD_TOKEN from a secret without shipping a config file,
    while local runs keep using config.yaml.
    """
    config_path = Path(__file__).parent / "config.yaml"
    config = {}

    if config_path.is_file():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        except yaml.YAMLError as err:
            sys.exit(f"Could not parse {config_path.name}: {err}\n")
        if not isinstance(config, dict):
            sys.exit(f"{config_path.name} must contain a mapping of keys to values.\n")

    config.update(config_from_env(os.environ))

    config.setdefault("PRIMARY_ACCOUNT_PREFIX", DEFAULT_PREFIX)

    missing = sorted(k for k in REQUIRED_CONFIG_KEYS if not config.get(k))
    if missing:
        sys.exit(
            "Missing required config: " + ", ".join(missing) + "\n"
            f"Set them as {ENV_PREFIX}* environment variables, or copy "
            "config.example.yaml to config.yaml and fill them in.\n"
        )
    return config


def setup_logging():
    """Set up rotating file logger for Discord bot."""
    logger = logging.getLogger('discord')
    if any(not isinstance(h, logging.NullHandler) for h in logger.handlers):
        return
    logger.setLevel(logging.INFO)
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(
        '[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

    # LOG_FILE='' disables file logging (containers log to stdout, and the root
    # filesystem may be read-only). Any other value is used as the path.
    log_file = os.environ.get('LOG_FILE', str(Path(__file__).parent / 'discord.log'))
    if log_file:
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file,
                encoding='utf-8',
                maxBytes=32 * 1024 * 1024,  # 32 MiB
                backupCount=5,
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError as err:
            print(f'File logging disabled ({log_file}): {err}', file=sys.stderr)

    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


class DiscordBot(commands.Bot):
    """Bot subclass so extensions load in setup_hook, as discord.py 2.x expects."""

    async def setup_hook(self) -> None:
        """Runs after login but before the gateway connects."""
        await self.load_extensions()

    async def load_extensions(self) -> None:
        """Load all bot modules/extensions from specified directories."""
        for dir_ in EXTENSION_DIRS:
            log.info('Attempting to load all extensions in %s directory ...', dir_.upper())

            dir_path = Path(__file__).parent / 'modules' / dir_
            if not dir_path.is_dir():
                log.warning('Directory %s does not exist.', dir_path)
                continue

            for filename in sorted(dir_path.iterdir()):
                if filename.suffix != '.py' or filename.stem in EXTENSION_EXCLUSIONS:
                    continue
                try:
                    await self.load_extension(f'modules.{dir_}.{filename.stem}')
                    log.info('Successfully loaded extension: %s', filename.stem)
                except commands.ExtensionAlreadyLoaded:
                    log.warning('Extension already loaded: %s', filename.stem)
                except commands.ExtensionNotFound:
                    log.error('Extension not found: %s', filename.stem)
                except commands.NoEntryPointError:
                    log.error('Extension missing setup(): %s', filename.stem)
                except commands.ExtensionFailed as err:
                    log.error('Extension failed to load: %s — %s: %s',
                              filename.stem, type(err.original).__name__, err.original)

        if EXTENSION_EXCLUSIONS:
            log.info('Excluded extensions: %s', ', '.join(EXTENSION_EXCLUSIONS))


async def main():
    """Configure logging, build the bot, and run it until disconnect."""
    setup_logging()

    config = load_config()
    token = config["DISCORD_TOKEN"]
    prefix = config["PRIMARY_ACCOUNT_PREFIX"]

    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    log.info('Initializing startup sequence ...')

    # Async context manager closes the HTTP session and gateway cleanly on exit
    async with DiscordBot(command_prefix=prefix, intents=intents, help_command=None) as bot:
        log.info('Attempting to log in to bot ...')
        try:
            await bot.start(token)
        except discord.LoginFailure as error:
            log.critical('Discord login failed: %s', error)
            sys.exit("Login Unsuccessful\n")
        except discord.PrivilegedIntentsRequired as error:
            log.critical('Privileged intents are not enabled in the Developer Portal: %s', error)
            sys.exit("Enable the Members and Message Content intents for this bot\n")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info('Shutdown requested — exiting.')
