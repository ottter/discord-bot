"""Gather current GE price of Runescape (3 & Old School) items"""
from discord.ui import Button, View
from discord.ext import commands
import discord
from discord import app_commands, ButtonStyle, Embed

from config import timestamp as TIME
from scripts.runescape.grandexchange import find_rs3_item

# https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Usage_and_APIs
# https://api.weirdgloop.org/

# class GrandExchangeMenu(discord.ui.view):
#     def __init__(self):
#         super().__init__()
#         self.value = None
    
#     @discord.ui.button(label="send", style=discord.ButtonStyle.blurple)
#     async def menu1(self, button: discord.ui.Button, interaction: discord.Interaction): 
#         await interaction.response.edit_message (content="This is a editited message")

#     @discord.ui.button(label="Edit Message", style=discord.ButtonStyle.green) 
#     async def menu2(self, button: discord.ui.Button, interaction: discord.Interaction): 
#         await interaction.response.edit_message (content="This is a editited message")

#     @discord.ui.button(label="Send Message", style=discord.ButtonStyle.grey)
#     async def menu3(self, button: discord.ui.Button, interaction: discord.Interaction): 
#         await interaction.response.edit_message (content="This is a editited message")

class GrandExchangeCmd(commands.Cog):
    """Provides user with RS3 and OSRS Grand Exchange info"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['rspc', 'rs3ge', 'rs3pc'])
    async def rsge(self, context):
        """Search RS3 GE"""
        values = find_rs3_item(context.message.content.split(" ", 1)[1])
        view = View()
        for value in values:
            button = Button(label=value, style=ButtonStyle.blurple)
            view.add_item(button)
        await context.send("items:", view=view)

    # @commands.cooldown(1, 3, commands.BucketType.user)
    # @commands.command(aliases=['ospc', '07ge', '07pc', 'ge', 'pc'])
    # async def osge(self, context):
    #     """Search OSRS GE"""
    #     item_request = context.message.content.split(" ", 1)[1]
    #     await search_grandexchange(context, 'osrs', item_request, embed=True)


async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(GrandExchangeCmd(bot))