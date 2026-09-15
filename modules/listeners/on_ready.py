"""Startup banner and one-time slash command sync."""
import logging

import discord
from discord.ext import commands

log = logging.getLogger('discord.bot')


class OnReadyListen(commands.Cog):
    """Reports connection details once the gateway is ready."""

    def __init__(self, bot):
        self.bot = bot
        self.synced = False

    @commands.Cog.listener()
    async def on_ready(self):
        """Fires on every connect, including reconnects."""
        guilds = self.bot.guilds
        log.info('Online as %s (%s) | prefix %s | %.0f ms | %s guild(s): %s',
                 self.bot.user, self.bot.user.id, self.bot.command_prefix,
                 self.bot.latency * 1000, len(guilds),
                 ', '.join(g.name for g in guilds) or 'none')

        # Syncing is rate limited, so only do it on the first connect.
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
