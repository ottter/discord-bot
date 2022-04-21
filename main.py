import config
import json
import time
import os
import discord
from discord.ext import commands


def get_prefix(client, message):
    try:
        with open('./files/prefix.json', 'r') as file:
            prefixes = json.load(file)
        return prefixes[str(message.guild.id)]
    except:
        return '.'


intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
bot = commands.Bot(command_prefix=config.PRIMARY_ACCOUNT_PREFIX, intents=intents)
# bot.remove_command('help')
# TODO: Improve the .help command; disabled until fixed


@bot.event
async def on_ready():
    if bot.user.name == config.DEV_ACCOUNT_NAME:
        bot.command_prefix = config.DEV_ACCOUNT_PREFIX

    print('='*34)
    print('Logged in as: ', bot.user.name)
    print('Client ID:    ', bot.user.id)
    print('Local time:   ', config.time)
    print('='*34)


@bot.command(hidden=True, pass_context=True)
async def ping(context):
    before = time.monotonic()
    message = await context.channel.send("Pong!")
    server_ping = int((time.monotonic() - before) * 1000)

    await message.edit(content=f'Ping: {server_ping}ms')
    print(f'{context.author} pinged the server: {server_ping}ms')


@bot.event
async def on_message(context):
    if context.author == bot.user:
        return
    await bot.process_commands(context)


def load_extensions():
    dir_list = ['listeners', 'modules']
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
    print('=== Initializing startup procedure ...')
    load_extensions()
    print(f'=== Attempting to log in to bot ...')
    try:
        bot.run(config.DISCORD_TOKEN)
    except Exception as error:
        print('\nDiscord: Unsuccessful login. Error: ', error)
        quit()


if __name__ == '__main__':
    log_in()
