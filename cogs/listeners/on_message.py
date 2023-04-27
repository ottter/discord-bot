import discord
from discord.ext import commands
from config import timestamp as TIME


class OnMessageListen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, context):
        """Ignore messages from self"""
        if context.author == self.bot.user:
            return


async def setup(bot):
    await bot.add_cog(OnMessageListen(bot))