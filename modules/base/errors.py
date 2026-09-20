"""Turns an unhandled command error into something safe to show the user."""
import logging
import uuid

import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger('discord.bot')


class Errors(commands.Cog):
    """Installs a tree-wide error handler, restoring the old one on unload."""

    def __init__(self, bot):
        self.bot = bot
        self.previous = bot.tree.on_error
        bot.tree.on_error = self.on_error

    async def cog_unload(self):
        self.bot.tree.on_error = self.previous

    async def on_error(self, interaction: discord.Interaction,
                       error: app_commands.AppCommandError) -> None:
        """Runs for any slash command that raises."""
        command = interaction.command.qualified_name if interaction.command else 'unknown'

        # Check failures are the user's problem, not a bug, and are safe to quote.
        if isinstance(error, app_commands.CheckFailure):
            log.info('%s was refused /%s: %s', interaction.user, command, error)
            await self._reply(interaction, str(error))
            return

        reference = uuid.uuid4().hex[:8]
        log.error('/%s failed for %s [%s]', command, interaction.user, reference,
                  exc_info=error)
        await self._reply(
            interaction,
            f'Something went wrong running that. If it keeps happening, quote `{reference}`.')

    @staticmethod
    async def _reply(interaction: discord.Interaction, message: str) -> None:
        """Answer whether or not the command already responded."""
        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException as err:
            log.warning('Could not report an error to %s: %s', interaction.user, err)


async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(Errors(bot))
