"""Gather current GE price of Runescape (3 & Old School) items"""
import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands, ButtonStyle, Embed

from config import timestamp as TIME
from scripts.runescape.grandexchange import find_rs3_item

# https://www.youtube.com/watch?v=82d9s8D6XE4
# HERE https://www.youtube.com/watch?v=kNUuYEWGOxA&t=903s 


class GrandExchangeSlash(commands.Cog):
    """Provides user with RS3 and OSRS Grand Exchange info"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rsge", description="RS3 Grand Exchange")
    async def rsge(interaction: discord.Interaction, item:str):
        """Search RS3 GE"""
        values = find_rs3_item(item)
        view = View()
        for value in values:
            button = Button(label=value, style=ButtonStyle.blurple)
            view.add_item(button)
        await interaction.response.send_message("items:", view=view, ephemeral=True)

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(GrandExchangeSlash(bot))