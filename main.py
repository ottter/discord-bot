"""
Remastered version of my original Discord bot, which I used to "learn" Python
This is the main setup file that is used to run the entire bot
Reference ./README.md for instructions and useful information
"""
import os
import sys
import asyncio
import discord
from discord.ext import commands

from config import PRIMARY_ACCOUNT_PREFIX, DISCORD_TOKEN
from config import timestamp as TIME


intents = discord.Intents.all()
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix=PRIMARY_ACCOUNT_PREFIX, intents=intents, help_command=None)

async def load_extensions(action, prnt=True):
    """Load all modules/extensions/cogs from specificed directories"""
    dir_list = ['commands', 'listeners', 'slashes']
    exclusion_list = ['help']
    for dir_ in dir_list:
        print(f'=== Attempting to load all extensions in {dir_.upper()} directory ...') if prnt else None
        for filename in os.listdir(f'./cogs/{dir_}'):
            module = filename[:-3]
            if filename.endswith('.py') and module not in exclusion_list:
                try:
                    await action(f'cogs.{dir_}.{module}')
                    print(f'\tSuccessfully loaded extension: {module}') if prnt else None
                except Exception as err:
                    exc = f'{type(err).__name__}: {err}'
                    print(f'\tFailed to load extension:  {module}\n\t\t{exc}') if prnt else None
    for excl_module in exclusion_list:
        print(f'=== Excluding the extension: {excl_module}') if prnt else None


async def log_in():
    """Boot process"""
    print('\n=== Initializing startup sequence ...')
    await load_extensions(action=bot.load_extension, prnt=True)
    print('=== Attempting to log in to bot ...')
    try:
        await bot.start(DISCORD_TOKEN)
    except discord.errors.HTTPException or discord.errors.LoginFailure as error:
        print('\nDiscord: Unsuccessful login:', error)
    else:
        sys.exit("Login Unsuccessful")


if __name__ == '__main__':
    asyncio.run(log_in())
