"""
Remastered version of my original Discord bot, which I used to "learn" Python
This is the main setup file that is used to run the entire bot
Reference ./README.md for instructions and useful information
"""
import sys
import yaml
import asyncio
import logging
import logging.handlers
import discord
from pathlib import Path
from discord.ext import commands
from utils import timestamp

REQUIRED_CONFIG_KEYS = {"DISCORD_TOKEN", "PRIMARY_ACCOUNT_PREFIX"}

log = logging.getLogger('discord.bot')


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    missing = REQUIRED_CONFIG_KEYS - config.keys()
    if missing:
        sys.exit(f"Missing required config keys: {', '.join(sorted(missing))}\n")
    return config


def setup_logging():
    """Set up rotating file logger for Discord bot."""
    logger = logging.getLogger('discord')
    if logger.handlers:
        return
    logger.setLevel(logging.INFO)
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

    file_handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


async def load_extensions(bot, action):
    """Load all bot modules/extensions from specified directories."""
    dir_list = ['commands', 'listeners', 'slashes']
    exclusion_list = ['help']

    for dir_ in dir_list:
        log.info('Attempting to load all extensions in %s directory ...', dir_.upper())

        dir_path = Path(__file__).parent / 'modules' / dir_
        if not dir_path.is_dir():
            log.warning('Directory %s does not exist.', dir_path)
            continue

        for filename in dir_path.iterdir():
            if filename.suffix != '.py' or filename.stem in exclusion_list:
                continue
            try:
                await action(f'modules.{dir_}.{filename.stem}')
                log.info('Successfully loaded extension: %s', filename.stem)
            except commands.ExtensionAlreadyLoaded:
                log.warning('Extension already loaded: %s', filename.stem)
            except commands.ExtensionNotFound:
                log.error('Extension not found: %s', filename.stem)
            except commands.NoEntryPointError:
                log.error('Extension missing setup(): %s', filename.stem)
            except commands.ExtensionFailed as err:
                log.error('Extension failed to load: %s — %s: %s', filename.stem, type(err.original).__name__, err.original)

    for excl_module in exclusion_list:
        log.info('Excluding extension: %s', excl_module)


async def main():
    setup_logging()

    config = load_config()
    token = config["DISCORD_TOKEN"]
    prefix = config["PRIMARY_ACCOUNT_PREFIX"]

    intents = discord.Intents.default()
    intents.members = True
    intents.reactions = True
    intents.message_content = True

    bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)

    log.info('Initializing startup sequence ...')
    await load_extensions(bot, action=bot.load_extension)
    log.info('Attempting to log in to bot ...')

    try:
        await bot.start(token)
    except discord.LoginFailure as error:
        log.critical('Discord login failed: %s', error)
        sys.exit("Login Unsuccessful\n")
    except asyncio.TimeoutError:
        log.critical('Login timed out. Please check token and network connection.')
        sys.exit("Login Unsuccessful\n")


if __name__ == '__main__':
    asyncio.run(main())
