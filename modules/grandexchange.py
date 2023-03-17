import discord
from discord.ext import commands

import config

# https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Usage_and_APIs

class GrandExchange(commands.Cog):
    """Provides user with random and relevant xkcd comics"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def rsge(self, context):
        return
    
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['07ge'])
    async def osge(self, context):
        return


def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(GrandExchange(bot))