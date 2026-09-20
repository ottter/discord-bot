"""Reports which build of the bot is running."""
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger('discord.bot')

# Set at build time from the git tag; see the Dockerfile and docker.yml.
# Running from a checkout there is no build, so say so rather than guess.
VERSION = os.environ.get('BOT_VERSION') or 'dev'


class Version(commands.Cog):
    """Answers the 'is the new image actually running?' question."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='version', description='Which version of the bot is running')
    async def version(self, interaction: discord.Interaction):
        """Anyone can run it; the answer is only shown to them."""
        await interaction.response.send_message(f'Current version: {VERSION}',
                                                ephemeral=True)


async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(Version(bot))
