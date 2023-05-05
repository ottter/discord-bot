"""Gather current GE price of Runescape (3 & Old School) items"""
import discord
from discord.ext import commands
from discord import app_commands

from config import timestamp as TIME
from scripts.runescape.grandexchange import find_item, grandexchange_builder
from scripts.runescape.ui_subclass import GrandExchangeView

# https://www.youtube.com/watch?v=82d9s8D6XE4
# HERE https://www.youtube.com/watch?v=kNUuYEWGOxA&t=903s 


class GrandExchangeSlash(commands.Cog):
    """Provides user with RS3 and OSRS Grand Exchange info"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rsge", description="Search items on the RS3 Grand Exchange")
    async def rsge(self, interaction: discord.Interaction, item:str):
        """Search RS3 GE"""
        content, embed, view = grandexchange_builder(author=interaction.user, 
                                                     game="osrs", 
                                                     item=item, 
                                                     file_path="data/runescape/rs3items.tsv")
        await interaction.response.send_message(content=content, embed=embed, view=view)

    @app_commands.command(name="osge", description="Search items on the OSRS Grand Exchange")
    async def rsge(self, interaction: discord.Interaction, item:str):
        """Search OSRS GE"""
        content, embed, view = grandexchange_builder(author=interaction.user, 
                                                     game="osrs", 
                                                     item=item, 
                                                     file_path="data/runescape/osrsitems.csv")
        await interaction.response.send_message(content=content, embed=embed, view=view)

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(GrandExchangeSlash(bot))