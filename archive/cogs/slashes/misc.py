"""Misc SLASH commands that aren't enough for their own file"""
import discord
from discord.ext import commands
from discord import app_commands

from config import timestamp as TIME

PASTA_FBI = ("I DECLARE THAT EVERY POST I HAVE EVER MADE ON THIS DISCORD IS SATIRE."
    " I DO NOT CONDONE NOR SUPPORT ANY OF THE OPINIONS EXPRESSED ON THIS CHATROOM.")


class MiscSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Say hello to dogdog")
    async def hello(self, interaction: discord.Interaction):
        """Say hello to the chatbot"""
        print(f"{TIME()}: {interaction.user} said hello to me")
        await interaction.response.send_message(f"Hey {interaction.user.mention}!", ephemeral=True)

    @app_commands.command(name="fbi", description="FBI disclaimer")
    async def fbi_pasta(self, interaction: discord.Interaction):
        """Say hello to the FBI"""
        print(f"{TIME()}: {interaction.user} used /fbi")
        await interaction.response.send_message(PASTA_FBI)

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(MiscSlash(bot))