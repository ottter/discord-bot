import config
import json
import time
import os
import re
import discord
from discord.ext import commands

import modules.admin


def get_prefix(client, message):
    try:
        with open('./files/prefix.json', 'r') as file:
            prefixes = json.load(file)
        return prefixes[str(message.guild.id)]
    except:
        return '.'


intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
# bot = commands.Bot(command_prefix=get_prefix)
bot = commands.Bot(command_prefix='.', intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():

    print('-'*34)
    print('Logged in as: ', bot.user.name)
    print('Client ID:    ', bot.user.id)
    print('Local time:   ', config.time)
    print('-'*34)


@bot.command(hidden=True, pass_context=True)
async def ping(context):
    before = time.monotonic()
    message = await context.channel.send("Pong!")
    server_ping = int((time.monotonic() - before) * 1000)

    await message.edit(content=f'Ping: {server_ping}ms')
    print(f'{context.author} pinged the server: {server_ping}ms')


@bot.event
async def on_message(context):
    message = str(context.content.lower())

    if context.author == bot.user:
        return

    # if context.channel.id == 786399511651287041 and re.search("(?i)(Wordle )\d{3}( )([3-6]|X)(\/6)", message):
    if re.search("(?i)(Wordle )\d{3}( )([3-6]|X)(\/6)", message):
        await context.send(f"Wordle loser {user.mention}")

#    if message.startswith('!co2'):
#        await context.channel.send('Also CO2 is good for plants, meaning more CO2 means more life-sustaining oxygen '
#                                   'and thus increase in agriculture as plants grow faster, more food, etc.')

    await bot.process_commands(context)


@bot.event
async def on_guild_join(guild):
    # TODO: Create server join message
    # with open('./files/prefix.json', 'r') as file:
    #     prefixes = json.load(file)
    # prefixes[str(guild.id)] = "."
    # with open('./files/prefix.json', 'w') as file:
    #     json.dump(prefixes, file, indent=4)
    print(f'joined new server: {guild}')


@bot.event
async def on_guild_remove(guild):
    # Removes the custom prefix from prefixes.json when bot is removed from a server
    # TODO: Get this to work with extensions
    with open('./files/prefix.json', 'r') as file:
        prefixes = json.load(file)
    prefixes.pop(str(guild.id))
    with open('./files/prefix.json', 'w') as file:
        json.dump(prefixes, file, indent=4)
    print(f'left server: {guild}')


@bot.event
async def on_member_remove(member):
    primary_server_base_id = None
    primary_welcome_channel = None
    if primary_server_base_id and member.guild.id == primary_server_base_id:
        channel = bot.get_channel(primary_welcome_channel)
        await channel.send(f'Cya {member} you dummy')


def load_extensions():
    # Loads all of the extensions. Note: check iDM if I branch out to multiple folders
    exclusion_list = []
    for filename in os.listdir('./modules'):
        module = filename[:-3]
        if filename.endswith('.py') and module not in exclusion_list:
            try:
                bot.load_extension(f'modules.{module}')
                print(f'Successfully loaded extension: {module}')
            except Exception as err:
                exc = f'{type(err).__name__}: {err}'
                print(f'Failed to load extension:  {module}\n{exc}')


def log_in():
    load_extensions()
    print('Attempting to log in...')
    try:
        bot.run(config.DISCORD_TOKEN)
    except Exception as error:
        print('Discord: Unsuccessful login. Error: ', error)
        quit()


if __name__ == '__main__':
    log_in()
