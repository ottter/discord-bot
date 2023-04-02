"""Custom HELP command instead of Discord's default"""
import discord
from discord.ext import commands


class Help(commands.Cog):
    """Lists all cogs and commands"""

    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name='help', pass_context=True, brief='help command')
    async def help(self, context, *cog):
        """Lists all cogs and commands"""

        try:
            if not cog:
                helper = discord.Embed(title='Cog Help',
                                       description='Use `.help *cog*` for more information')
                module_desc = ''

                for _x in self.client.cogs:
                    module_desc += f'{_x} - {self.client.cogs[_x].__doc__}\n'

                helper.add_field(
                    name='Cogs',
                    value=module_desc[0:len(module_desc) - 1],
                    inline=False)
                command_desc = ''

                for command_call in self.client.walk_commands():
                    if not command_call.cog_name and not command_call.hidden:
                        command_desc += f'{command_call.name} - {command_call.help}\n'

                # If commands are in main.py
                # helper.add_field(name='Misc Commands',
                #                  value=command_desc[0:len(command_desc)-1],
                #                  inline=False)

                await context.message.author.send('', embed=helper)
                await context.message.add_reaction(emoji='✉')
            else:
                if len(cog) > 1:
                    helper = discord.Embed(description='Error! Too many requests',
                                           color=discord.Color.red())
                    await context.message.author.send('', embed=helper)

                else:
                    found = False
                    variable = ((_x, _y) for _x in self.client.cogs for _y in cog if _x == _y)
                    cmd_desc = self.client.cogs[cog[0]].__doc__

                    for _x, _y in variable:
                        helper = discord.Embed(title=f'{cog[0]} Command Listing',
                                               description=cmd_desc)
                        for cmd in self.client.get_cog(_y).get_commands():
                            if not cmd.hidden:
                                helper.add_field(name=cmd.name, value=cmd.help, inline=False)
                        found = True

                    if not found:
                        helper = discord.Embed(description=f'Error! The {cog[0]} cog can not be found',
                                               color=discord.Color.red())

                    await context.message.author.send('', embed=helper)
                    await context.message.add_reaction(emoji='✉')
        except:
            pass


def setup(client):
    """Adds the cog (module) to startup. See main/load_extensions"""
    client.add_cog(Help(client))
