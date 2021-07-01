import config
import json
import time
import os
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
    server_ping = f'Ping: {int((time.monotonic() - before) * 1000)}ms'

    await message.edit(content=server_ping)
    print(f'{context.author} pinged the server: {server_ping}')


@bot.event
async def on_message(context):
    message = str(context.content.lower())

    if context.author == bot.user:
        return

    if message.find('!co2') != -1:
        await context.channel.send('Also CO2 is good for plants, meaning more CO2 means more life-sustaining oxygen '
                                   'and thus increase in agriculture as plants grow faster, more food, etc.')

    # Lightscord specific on-messages
    if context.guild.id == 563549980439347201:
        if context.author.id == 209385907101368322:
            await context.author.edit(nick="Ellie")

    await bot.process_commands(context)


@bot.event
async def on_guild_join(guild):
    # TODO: Create server join message
    with open('./files/prefix.json', 'r') as file:
        prefixes = json.load(file)
    prefixes[str(guild.id)] = "."
    with open('./files/prefix.json', 'w') as file:
        json.dump(prefixes, file, indent=4)
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
    philoco = 563549980439347201
    welcome = 703752970894049320
    if member.guild.id == philoco:
        channel = bot.get_channel(welcome)
        await channel.send(f'Cya {member} you dummy')

        # Logic to automatically reinvite (and unban) users who leave
        if member not in modules.admin.banned_users:
            if member.guild.fetch_ban(member):
                await member.guild.unban(member)
                print(f'automatically unbanned {member}')
            invite_link = await channel.create_invite(max_age=1000)
            invite_channel = await member.create_dm()
            await invite_channel.send(f'wait come back lol {invite_link}')


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
