"""Gather current GE price of Runescape (3 & Old School) items"""
from discord.ext import commands

from config import timestamp as TIME
from scripts.runescape.grandexchange import find_item
from scripts.runescape.ui_subclass import GrandExchangeView, create_embed, preselect_embed

# https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Usage_and_APIs
# https://api.weirdgloop.org/

def grandexchange_builder(context, game, file_path):
    item = context.message.content.split(" ", 1)[1]
    closest_items = find_item(item, file_path=file_path)

    print(f"{TIME()}: Request for {game.upper()} [{item}] returned: {closest_items}")
    if len(closest_items) == 1:
        view = None         # Provide no buttons because there is only one item returned
        embed = create_embed(closest_items[0], game)
    else:
        view = GrandExchangeView(context.message.author, closest_items, game)
        embed = preselect_embed(game)
    return context.reply(view=view, embed=embed)


class GrandExchangeCmd(commands.Cog):
    """Provides user with RS3 and OSRS Grand Exchange info"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['rspc', 'rs3ge', 'rs3pc'])
    async def rsge(self, context):
        """Search RS3 GE"""
        await grandexchange_builder(context, game="rs", 
                                    file_path="data/runescape/rs3items.tsv")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['ospc', '07ge', '07pc', 'ge', 'pc'])
    async def osge(self, context):
        """Search OSRS GE"""
        await grandexchange_builder(context, game="osrs", 
                                    file_path="data/runescape/osrsitems.csv")

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(GrandExchangeCmd(bot))