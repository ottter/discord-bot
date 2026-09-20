"""Misc slash commands that aren't enough for their own file"""
import logging

import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger('discord.bot')

PASTA_FBI = (
    "I DECLARE THAT EVERY POST I HAVE EVER MADE ON THIS DISCORD IS SATIRE."
    " I DO NOT CONDONE NOR SUPPORT ANY OF THE OPINIONS EXPRESSED ON THIS CHATROOM."
)


class MiscSlash(commands.Cog):
    """Odds and ends too small to deserve their own file."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Say hello to dogdog")
    async def hello(self, interaction: discord.Interaction):
        """Says hello back, only to the person who asked."""
        log.info('%s used /hello', interaction.user)
        await interaction.response.send_message(f"Hey {interaction.user.mention}!", ephemeral=True)

    @app_commands.command(name="fbi", description="FBI disclaimer")
    async def fbi_pasta(self, interaction: discord.Interaction):
        """Posts the satire disclaimer copypasta."""
        log.info('%s used /fbi', interaction.user)
        await interaction.response.send_message(PASTA_FBI)


async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(MiscSlash(bot))
