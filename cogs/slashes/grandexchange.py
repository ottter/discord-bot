"""Gather current GE price of Runescape (3 & Old School) items"""
import discord
from discord.ext import commands
from discord import app_commands

from config import timestamp as TIME
from scripts.runescape.grandexchange import find_rs3_item
from scripts.runescape.ui_subclass import GrandExchangeView

# https://www.youtube.com/watch?v=82d9s8D6XE4
# HERE https://www.youtube.com/watch?v=kNUuYEWGOxA&t=903s 


class GrandExchangeSlash(commands.Cog):
    """Provides user with RS3 and OSRS Grand Exchange info"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rsge", description="RS3 Grand Exchange")
    async def rsge(self, interaction: discord.Interaction, item:str):
        """Search RS3 GE"""
        closest_items = find_rs3_item(item)
        view = GrandExchangeView(interaction.author, closest_items)
        content = "RS3 Grand Exchange\n Pick your item or refine your search"
        await self.context.send(content=content, view=view)

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(GrandExchangeSlash(bot))