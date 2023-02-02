"""
Remastered version of my original Discord bot, which I used to "learn" Python
This is the main setup file that is used to run the entire bot
Reference ./README.md for instructions and useful information
"""
import os
import sys
import json
import discord
from discord.ext import commands
from discord_slash import SlashCommand

from config import PRIMARY_ACCOUNT_PREFIX, DEV_ACCOUNT_NAME, DEV_ACCOUNT_PREFIX, DISCORD_TOKEN, TIME


def get_prefix(message):
    """LEGACY set the server-custom prefix used to run commands"""
    try:
        with open('./files/prefix.json', 'r', encoding="utf-8") as file:
            prefixes = json.load(file)
        return prefixes[str(message.guild.id)]
    except Exception:
        return "."


intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
bot = commands.Bot(command_prefix=PRIMARY_ACCOUNT_PREFIX, intents=intents)
slash = SlashCommand(bot, sync_commands=True)
# bot.remove_command('help')

@bot.event
async def on_ready():
    """Runs if login attempt is successful"""
    if bot.user.name == DEV_ACCOUNT_NAME:
        bot.command_prefix = DEV_ACCOUNT_PREFIX

    print('='*34)
    print('Logged in as: ', bot.user.name)
    print('Client ID:    ', bot.user.id)
    print('Local time:   ', TIME)
    print('='*34, '\n'*2)


@bot.command(hidden=True, pass_context=True)
async def ping(context):
    """Test latency"""
    server_ping = round(bot.latency * 1000)
    await context.channel.send(f"Ping: {server_ping}ms")
    print(f'{context.author} pinged the server: {server_ping}ms')


@bot.event
async def on_message(context):
    """Ignore messages from self"""
    if context.author == bot.user:
        return
    # await bot.process_commands(context)


def load_extensions():
    """Load all modules/extensions/cogs from specificed directories"""
    dir_list = ['listeners', 'modules', 'slashes']
    exclusion_list = ['help']
    for dir_ in dir_list:
        print(f'=== Attempting to load all extensions in {dir_} directory ...')
        for filename in os.listdir(f'./{dir_}'):
            module = filename[:-3]
            if filename.endswith('.py') and module not in exclusion_list:
                try:
                    bot.load_extension(f'{dir_}.{module}')
                    print(f'\tSuccessfully loaded extension: {module}')
                except Exception as err:
                    exc = f'{type(err).__name__}: {err}'
                    print(f'\tFailed to load extension:  {module}\n\t\t{exc}')
    for excl_module in exclusion_list:
        print(f'=== Excluding the extension: {excl_module}')


def log_in():
    """Login function"""
    print('=== Initializing startup sequence ...')
    load_extensions()
    print('=== Attempting to log in to bot ...')
    try:
        bot.run(DISCORD_TOKEN)
    except discord.errors.HTTPException or discord.errors.LoginFailure as error:
        print('\nDiscord: Unsuccessful login:', error)
    else:
        sys.exit("Login Unsuccessful")


if __name__ == '__main__':
    log_in()
