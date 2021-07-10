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
    server_ping = int((time.monotonic() - before) * 1000)

    await message.edit(content=f'Ping: {server_ping}ms')
    print(f'{context.author} pinged the server: {server_ping}ms')


@bot.event
async def on_message(context):
    message = str(context.content.lower())

    if context.author == bot.user:
        return

    if message.find('!co2') != -1:
        await context.channel.send('Also CO2 is good for plants, meaning more CO2 means more life-sustaining oxygen '
                                   'and thus increase in agriculture as plants grow faster, more food, etc.')

    # Guild specific on-messages
    if context.guild:
        # Lightscord specific on-messages
        if context.guild.id == 563549980439347201:
            if context.author.id == 209385907101368322:         # twil
                await context.author.edit(nick="Ellie")

            # add some flair
            # if context.channel.id == 570085619376848906:        # steamies
            #     if context.author.id == 178563304321581056:     # jeb
            #         await context.add_reaction('🌈')

            # ban jebbers from steamies
            # if context.channel.id == 570085619376848906:
            #     if context.author.id == 178563304321581056:
            #         await context.delete()

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
async def on_member_update(before, after):
    # I'll put this in a table eventually...
    auto_roller_add = {
        657117149612998657: ['Admin', 'Redpilled', 'STEM'],             # gabe
        436331384240472075: ['Admin', 'Redpilled', 'STEM'],             # dodo
        150125122408153088: ['fun, loving individual', 'STEM'],         # james
        273532188803203072: ['fun, loving individual', 'STEM'],         # morgan
        240046314321084417: ['Austistic', 'STEM', 'Book Club'],         # zin
        209385907101368322: ['Injun', 'STEM', 'Book Club', 'LGBTQ+'],   # twil
        149187078981287936: ['Doctor Of Philosophy', 'STEM'],           # miles
        328043851891605506: ['Walmart Ambassador', 'Rap Champion', 'STEM']  # saj
    }
    auto_roller_rm = {
        657117149612998657: ['whale'],    # gabe
    }

    # Role fixer
    role_diff = list(set(before.roles) - set(after.roles)) + list(set(after.roles) - set(before.roles))
    if before.guild.id == 563549980439347201:   # lightscord
        for role in role_diff:
            if role.name in auto_roller_add[before.id]:
                try:
                    await after.add_roles(role)
                except Exception as err:
                    print(f'Couldn\'t fix the role situation, but this might help:{err}')
                    continue
            if role.name in auto_roller_rm[before.id]:
                try:
                    await after.remove_roles(role)
                except Exception as err:
                    print(f'Couldn\'t fix the role situation, but this might help:{err}')
                    continue
            else:
                pass


@bot.event
async def on_member_remove(member):
    philoco = 563549980439347201
    welcome = 703752970894049320
    if member.guild.id == philoco:
        channel = bot.get_channel(welcome)
        await channel.send(f'Cya {member} you dummy')

        # Logic to automatically reinvite (and unban) users who leave
        if member not in modules.admin.banned_users:
            try:
                await member.guild.unban(member)
                print(f'automatically unbanned {member}')
            except:
                pass
            invite_link = await channel.create_invite(max_age=1000)
            invite_channel = await member.create_dm()
            await invite_channel.send(f'wait come back lol {invite_link}')


@bot.event
async def on_message_delete(message):
    easter_egg_but_not_really_well_hidden = ''
    if message.author.bot is True:
        easter_egg_but_not_really_well_hidden = f'but it\'s a bot so who cares?\n**Message**: {message.content}'
    await message.channel.send(f'A message from **{message.author.name}** was deleted '
                               f'{easter_egg_but_not_really_well_hidden}')
    # Removed this until I can tell difference between user deletion and admin abuse
    # await message.channel.send(f'A message from **{message.author.name}** was deleted '
    #                            f'{easter_egg_but_not_really_well_hidden}\n**Message**: {message.content}')


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
