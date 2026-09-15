import logging

import discord
from discord.ext import commands

log = logging.getLogger('discord.bot')


class OnReadyListen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.info('=' * 46)
        log.info('ONLINE - connected to Discord successfully')
        log.info('Username   : %s', self.bot.user)
        log.info('Client ID  : %s', self.bot.user.id)
        log.info('Cmd Prefix : %s', self.bot.command_prefix)
        log.info('Latency    : %.0f ms', self.bot.latency * 1000)
        log.info('Guilds     : %s', len(self.bot.guilds))
        for guild in self.bot.guilds:
            log.info('  - %s (%s)', guild.name, guild.id)

        try:
            synced = await self.bot.tree.sync()
            log.info('Slash cmds : %s synced (%s)',
                     len(synced), ', '.join(sorted(c.name for c in synced)) or 'none')
        except discord.HTTPException as err:
            log.error('Failed to sync command tree: %s', err)

        log.info('Bot is ready. Press Ctrl+C to stop.')
        log.info('=' * 46)


async def setup(bot):
    await bot.add_cog(OnReadyListen(bot))
