"""Gather current GE price of Runescape (3 & Old School) items"""
from scripts.runescape.grandexchange import search_grandexchange
from discord.ext import commands

# https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Usage_and_APIs
# https://api.weirdgloop.org/

class GrandExchangeCmd(commands.Cog):
    """Provides user with RS3 and OSRS Grand Exchange info"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['rspc', 'rs3ge', 'rs3pc'])
    async def rsge(self, context):
        """Search RS3 GE"""
        item_request = context.message.content.split(" ", 1)[1]
        await search_grandexchange(context, 'rs', item_request, embed=True)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['ospc', '07ge', '07pc', 'ge', 'pc'])
    async def osge(self, context):
        """Search OSRS GE"""
        item_request = context.message.content.split(" ", 1)[1]
        await search_grandexchange(context, 'osrs', item_request, embed=True)


async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(GrandExchangeCmd(bot))