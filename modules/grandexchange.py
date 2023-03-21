"""Gather current GE price of Runescape (3 & Old School) items"""
import discord
from discord.ext import commands
import requests
import config

# https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Usage_and_APIs
# https://api.weirdgloop.org/

def import_item(game, item):
    base_url = f"https://api.weirdgloop.org/exchange/history/{game}/latest?name={item}"
    headers = {
        'User-Agent': 'github/ottter-discord-bot' }     # Owners of API request for a custom user-agent
    response = requests.get(url=base_url, headers=headers).json()
    return response

def search_grandexchange(context, game, item, embed=True):
    output = import_item(game, item)
    # Example: {'Cannonball': {'id': '2', 'timestamp': '2023-03-19T03:00:45.000Z', 'price': 160, 'volume': 20665706}}
    item_name = list(output.keys())[0]
    if not embed:
        return create_text(context, output, item_name)
    embed = create_embed(output, game, item_name)
    return context.send(embed=embed)

def create_text(context, output, item_name):
    price = '{:,}'.format(output[item_name]['price'])
    volume = output[item_name]['volume']
    textblock = f"""**{item_name}**\nPrice: {price}\t Volume: {volume}"""
    return context.send(textblock)

def create_embed(output, game, item_name):
    game = "oldschool." if game == "osrs" else ''
    embed=discord.Embed(title=item_name, url=f"https://{game}runescape.wiki/w/{item_name.replace(' ', '_')}")
    embed.set_thumbnail(url=f"https://{game}runescape.wiki/images/{item_name.replace(' ', '_')}.png")
    embed.add_field(name="price", value='{:,}'.format(output[item_name]['price']), inline=True)
    embed.add_field(name="volume", value=output[item_name]['volume'], inline=True)
    return embed

class GrandExchange(commands.Cog):
    """Provides user with random and relevant xkcd comics"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def rsge(self, context):
        item_request = context.message.content.split(" ", 1)[1]
        await search_grandexchange(context, 'rs', item_request)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['07ge'])
    async def osge(self, context):
        item_request = context.message.content.split(" ", 1)[1]
        await search_grandexchange(context, 'osrs', item_request)


def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(GrandExchange(bot))
