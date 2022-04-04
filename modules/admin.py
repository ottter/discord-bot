from discord.ext import commands
from discord import Game
import discord
import config
import json

bot_admins = [
    '150125122408153089',   # me
]

MODULE_SUBDIR = 'modules'
FILES_SUBDIR = 'data'


class Admin(commands.Cog):
    """Basic bot admin-level controls"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def change_prefix(self, context, prefix):
        """Custom prefixes on a per-server basis in order to prevent command overlap"""
        # TODO: Change prefix quantifier (right word?) to utilize RegEx for non-alphanumeric keyboard characters
        if str(context.message.author.id) in bot_admins:
            if len(prefix) == 1:
                with open(f'./{FILES_SUBDIR}/prefixes.json', 'r') as file:
                    prefixes = json.load(file)
                prefixes[str(context.guild.id)] = prefix
                with open(f'./{FILES_SUBDIR}/prefixes.json', 'w') as file:
                    json.dump(prefixes, file, indent=4)
                await context.send(f'Prefix changed to: {prefix}')
            else:
                await context.send(f'Entry is not a valid prefix')

    @commands.command(pass_context=True)
    async def reload(self, context, module: str):
        """Reload the specified cog [off then on]"""
        if str(context.message.author.id) in bot_admins:
            try:
                self.bot.reload_extension(f'{MODULE_SUBDIR}.{module}')
                await context.send(f'Reloaded: {module}')
            except Exception as err:
                print('{}: {}'.format(type(err).__name__, err))
                await context.send(err)
        else:
            await context.send('You don\'t have permission to do that')

    @commands.command(pass_context=True)
    async def load(self, context, module: str):
        """Loads the specified cog [on]"""
        if str(context.message.author.id) in bot_admins:
            try:
                self.bot.load_extension(f'{MODULE_SUBDIR}.{module}')
                await context.send(f'Reloaded: {module}')
            except Exception as err:
                print('{}: {}'.format(type(err).__name__, err))
                await context.send(err)
        else:
            await context.send('You don\'t have permission to do that')

    @commands.command(pass_context=True)
    async def unload(self, context, module: str):
        """Unloads the specified cog [off]"""
        if str(context.message.author.id) in bot_admins:
            try:
                self.bot.unload_extension(f'{MODULE_SUBDIR}.{module}')
                await context.send(f'Unloaded: {module}')
            except Exception as err:
                print('{}: {}'.format(type(err).__name__, err))
                await context.send('Error unloading cog')
        else:
            await context.send('You don\'t have permission to do that')

    @commands.command(pass_context=True)
    async def game(self, context):
        """Changes the 'game played' status message"""
        if str(context.message.author.id) in bot_admins:
            user_input = context.message.content.split(' ', 1)
            if user_input[1] == 'default'.lower():
                return await self.bot.change_presence(activity=Game(name=config.discord_game_played))
            await self.bot.change_presence(activity=Game(name=user_input[1]))

    @commands.command(pass_context=True)
    async def admin(self, context):
        """Lists the possible admin controls"""
        if str(context.message.author.id) in bot_admins:
            cog = ('Admin',)
            variable = ((x, y) for x in self.bot.cogs for y in cog if x == y)

            for x, y in variable:
                helper = discord.Embed(title='Admin Commands')
                for cmd in self.bot.get_cog(y).get_commands():
                    if not cmd.hidden:
                        helper.add_field(name=cmd.name, value=cmd.help, inline=False)

            await context.message.author.send('', embed=helper)
        else:
            await context.send('Bot Admin Only')

    @commands.command(hidden=True)
    async def shutdown(self, context):
        if str(context.message.author.id) in bot_admins:
            print('Shutting down...')
            await self.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
