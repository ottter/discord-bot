import logging

from discord.ext import commands

log = logging.getLogger('discord.bot')


class OnReadyListen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.info('=== Bot ready ===')
        log.info('Username   : %s', self.bot.user.name)
        log.info('Client ID  : %s', self.bot.user.id)
        log.info('Cmd Prefix : %s', self.bot.command_prefix)
        log.info('=================')

        try:
            await self.bot.tree.sync()
            log.info('Command tree synced successfully.')
        except Exception as err:
            log.error('Failed to sync command tree: %s', err)


async def setup(bot):
    await bot.add_cog(OnReadyListen(bot))
