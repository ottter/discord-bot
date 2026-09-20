"""Logs the startup banner and syncs slash commands once."""
import logging

import discord
from discord.ext import commands

log = logging.getLogger('discord.bot')


class OnReadyListen(commands.Cog):
    """Handles what happens once the gateway connects."""

    def __init__(self, bot):
        self.bot = bot
        self.synced = False

    @commands.Cog.listener()
    async def on_ready(self):
        """Also fires on reconnects, not just startup."""
        guilds = self.bot.guilds
        log.info('Online as %s (%s) | prefix %s | %.0f ms | %s guild(s): %s',
                 self.bot.user, self.bot.user.id, self.bot.command_prefix,
                 self.bot.latency * 1000, len(guilds),
                 ', '.join(g.name for g in guilds) or 'none')

        activity = self.bot.config.get('DEFAULT_ACTIVITY')
        if activity:
            await self.bot.change_presence(activity=discord.Game(name=activity))

        # Syncing is rate limited; once per process is enough.
        if self.synced:
            return
        try:
            synced = await self.bot.tree.sync()
            self.synced = True
            log.info('Synced %s slash command(s): %s', len(synced),
                     ', '.join(sorted(c.name for c in synced)) or 'none')
        except discord.HTTPException as err:
            log.error('Could not sync command tree: %s', err)


async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(OnReadyListen(bot))
