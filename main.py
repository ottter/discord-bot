"""
Remastered version of my original Discord bot, which I used to "learn" Python
This is the main setup file that is used to run the entire bot
Reference ./README.md for instructions and useful information
"""
import os
import sys
import time
import yaml
import asyncio
import logging
import logging.handlers
import discord
import datetime
from discord.ext import commands
from aiohttp import ClientSession


with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

PRIMARY_ACCOUNT_PREFIX = config["PRIMARY_ACCOUNT_PREFIX"]
DISCORD_TOKEN = config["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.message_content = True

bot = commands.Bot(command_prefix=PRIMARY_ACCOUNT_PREFIX, intents=intents, help_command=None)

def timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")

def setup_logging():
    """Set up rotating file logger for Discord bot."""
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,              # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

@bot.event
async def on_ready():
    """Confirm successful login when the bot is ready."""
    print(f"\nSuccessfully logged in as {bot.user} at {time.strftime('%Y-%m-%d %H:%M:%S')}")

async def load_extensions(action):
    """Load all bot modules/extensions from specified directories."""
    dir_list = ['commands', 'listeners', 'slashes']
    exclusion_list = ['help']

    for dir_ in dir_list:
        print(f'=== Attempting to load all extensions in {dir_.upper()} directory ...')
        
        dir_path = f'./modules/{dir_}'
        try:
            files = os.listdir(dir_path)
        except FileNotFoundError:
            print(f'Warning: Directory {dir_path} does not exist.')
            continue

        for filename in files:
            module = filename[:-3]
            if filename.endswith('.py') and module not in exclusion_list:
                try:
                    await action(f'modules.{dir_}.{module}')
                    print(f'\tSuccessfully loaded extension: {module}')
                except Exception as err:
                    exc = f'{type(err).__name__}: {err}'
                    print(f'\tFailed to load extension: {module}\n\t\t{exc}')
    
    for excl_module in exclusion_list:
        print(f'=== Excluding the extension: {excl_module}')

async def main():
    setup_logging()

    print('\n=== Initializing startup sequence ...')
    await load_extensions(action=bot.load_extension)
    print('=== Attempting to log in to bot ...')
    
    async with ClientSession() as client_session:
        try:
            await bot.start(DISCORD_TOKEN)
        except (discord.errors.HTTPException, discord.errors.LoginFailure) as error:
            print('Discord: Unsuccessful login:', error)
            sys.exit("Login Unsuccessful\n")
        except asyncio.TimeoutError:
            print("Login timed out. Please check token and network connection.")
            sys.exit("Login Unsuccessful\n")

# Run main function
if __name__ == '__main__':
    asyncio.run(main())