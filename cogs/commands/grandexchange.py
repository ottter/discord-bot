"""Gather current GE price of Runescape (3 & Old School) items"""
from discord.ext import commands

from config import timestamp as TIME
from scripts.runescape.grandexchange import find_item
from scripts.runescape.ui_subclass import GrandExchangeView, create_embed

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
        game = "rs"
        item = context.message.content.split(" ", 1)[1]
        closest_items = find_item(item, file_path='data/rs3items.tsv')
        print(f"{TIME()}: Request for {game.upper()} {item} returned: {closest_items}")

        if len(closest_items) == 1:
            embed = create_embed(closest_items[0], game)
            view, content = None, None
        else:
            view = GrandExchangeView(context.message.author, closest_items, game)
            content = "RS3 Grand Exchange\nPick your item or refine your search"
            embed = None
        await context.reply(content=content, view=view, embed=embed)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['ospc', '07ge', '07pc', 'ge', 'pc'])
    async def osge(self, context):
        """Search OSRS GE"""
        game = "osrs"
        item = context.message.content.split(" ", 1)[1]
        closest_items = find_item(item, file_path='data/osrsitems.csv')

        print(f"{TIME()}: Request for {game.upper()} {item} returned: {closest_items}")
        if len(closest_items) == 1:
            embed = create_embed(closest_items[0], game)
            view, content = None, None
        else:
            view = GrandExchangeView(context.message.author, closest_items, game)
            content = "OSRS Grand Exchange\nPick your item or refine your search"
            embed = None
        await context.reply(content=content, view=view, embed=embed)

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(GrandExchangeCmd(bot))