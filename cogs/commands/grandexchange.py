"""Gather current GE price of Runescape (3 & Old School) items"""
from discord.ext import commands

from scripts.runescape.grandexchange import grandexchange_builder

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
        item = context.message.content.split(" ", 1)[1]
        content, embed, view = grandexchange_builder(author=context.message.author, 
                                                     game="rs", 
                                                     item=item, 
                                                     file_path="data/runescape/rs3items.tsv")
        await context.reply(view=view, embed=embed, content=content)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['ospc', '07ge', '07pc', 'ge', 'pc'])
    async def osge(self, context):
        """Search OSRS GE"""
        item = context.message.content.split(" ", 1)[1]
        content, embed, view = grandexchange_builder(author=context.message.author, 
                                                     game="osrs", 
                                                     item=item, 
                                                     file_path="data/runescape/osrsitems.csv")
        print(content, embed, view)
        await context.reply(view=view, embed=embed, content=content)

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(GrandExchangeCmd(bot))