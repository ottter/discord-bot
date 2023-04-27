"""Misc SLASH commands that aren't enough for their own file"""
import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Cog

from config import timestamp as TIME


class MiscSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Say hello to dogdog")
    async def hello(self, interaction: discord.Interaction):
        """Say hello to the chatbot"""
        print(f"{TIME()}: {interaction.user.name} said hello to me")
        await interaction.response.send_message(f"Hey {interaction.user.mention}!", ephemeral=True)

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(MiscSlash(bot))