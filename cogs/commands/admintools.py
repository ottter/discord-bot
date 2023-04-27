"""BOT admin commands. Not to be confused with SERVER admins"""
import os
import discord
from discord.ext import commands

from config import BOT_ADMINS, DEFAULT_ACTIVITY, MODULE_SUBDIR
from config import timestamp as TIME


def is_admin(context):
    """Check if the user is considered a BOT admin"""
    if str(context.author.id) not in BOT_ADMINS:
        print(f'{TIME()}: {context.author} tried to use an admin command and failed.')
        return False
    return True

def select_all_modules(context, action, action_str):
    """Use * to perform action across all modules"""
    for filename in os.listdir('./modules'):
        module = filename[:-3]
        if filename.endswith('.py'):
            try:
                action(f'modules.{module}')
            except Exception as err:
                exc = f'{type(err).__name__}: {err}'
                print(f'{TIME()}: Failed to {action_str} extension:  {module}\n\t{exc}')

    print(f'{context.author} {action_str}ed all extensions')
    return context.send(f'{action_str.capitalize()}ed all modules.')

class AdminToolsCmd(commands.Cog):
    """Basic bot admin-level controls"""

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(alias='refresh', pass_context=True)
    async def reload(self, context, module: str):
        """Reload the specified cog [off then on]"""
        if module == '*':
            return await select_all_modules(context, self.bot.reload_extension, 'reload')

        try:
            self.bot.reload_extension(f'{MODULE_SUBDIR}.{module}')
            await context.send(f'Reloaded module: {module}')

        except Exception as err:
            print(f'{type(err).__name__}: {err}')
            await context.send(f'Could not reload: {module}')

    @commands.command(pass_context=True)
    async def load(self, context, module: str):
        """Loads the specified cog [on]"""
        if is_admin(context) is False:
            return context.send("I'm afraid that is something I can not allow to happen")

        if module == '*':
            return await select_all_modules(context, self.bot.load_extension, 'load')

        try:
            self.bot.load_extension(f'{MODULE_SUBDIR}.{module}')
            return await context.send(f'Reloaded: {module}')
        except Exception as err:
            print(f'{type(err).__name__}: {err}')
            return await context.send(err)

    @commands.command(pass_context=True)
    async def unload(self, context, module: str):
        """Unloads the specified cog [off]"""
        if await is_admin(context) is False:
            return

        if module == '*':
            return await select_all_modules(context, self.bot.unload_extension, 'unload')

        try:
            self.bot.unload_extension(f'{MODULE_SUBDIR}.{module}')
            await context.send(f'Unloaded: {module}')
        except Exception as err:
            print(f'{type(err).__name__}: {err}')
            await context.send('Error unloading cog')

    @commands.command(pass_context=True)
    async def discord_status(self, context):
        """Changes the current status message"""
        if not await is_admin(context):
            return

        user_input = context.message.content.split(' ', 1)
        if user_input[1] == 'default'.lower():
            return await self.bot.change_presence(activity=discord.Game(DEFAULT_ACTIVITY))
        await self.bot.change_presence(activity=discord.Game(user_input[1]))

    @commands.command(pass_context=True)
    async def admin(self, context):
        """Lists the possible admin controls"""
        if await is_admin(context) is False:
            return

        cog = ('Admin',)
        variable = ((_x, _y) for _x in self.bot.cogs for _y in cog if _x == _y)

        for _x, _y in variable:
            helper = discord.Embed(title='Admin Commands')
            for cmd in self.bot.get_cog(_y).get_commands():
                if not cmd.hidden:
                    helper.add_field(name=cmd.name, value=cmd.help, inline=False)
        await context.send('', embed=helper)

    @commands.command(hidden=True)
    async def shutdown(self, context):
        """Shutdown the bot. Can only be restarted through host"""
        if await is_admin(context) is False:
            return

        print('Shutting down...')
        await self.bot.logout()


async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(AdminToolsCmd(bot))