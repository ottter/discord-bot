"""Gather current GE price of Runescape (3 & Old School) items"""
import discord
from discord.ext import commands
import requests

# https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Usage_and_APIs
# https://api.weirdgloop.org/

def import_item(game, item):
    """Contact API to gather item information"""
    base_url = f"https://api.weirdgloop.org/exchange/history/{game}/latest?name={item}"
    headers = {
        # Owners of API request for a custom user-agent
        'User-Agent': 'github/ottter-discord-bot' }
    response = requests.get(url=base_url, headers=headers).json()
    return response

def search_grandexchange(context, game, item, embed=True):
    """Search the GE for requested item and return results to chat"""
    output = import_item(game, item)
    # Example: {'Cannonball': {'id': '2', 'timestamp': '2023-03-19T03:00:45.000Z', 
    #                          'price': 160, 'volume': 20665706}}
    item_name = list(output.keys())[0]
    if not embed:
        return create_text(context, output, item_name)
    embed = create_embed(output, game, item_name)
    return context.send(embed=embed)

def create_text(context, output, item_name):
    """Create the textblock for output, if embed argument is false"""
    price = '{:,}'.format(output[item_name]['price'])
    volume = output[item_name]['volume']
    textblock = f"**{item_name}**\nPrice: {price}\t Volume: {volume}"
    return context.send(textblock)

def create_embed(output, game, item_name):
    """Create the embed that gets returned to Discord. Embed by default"""
    game = "oldschool." if game == "osrs" else ''
    core_url = f"https://{game}runescape.wiki"
    embed=discord.Embed(title=item_name, url=f"{core_url}/w/{item_name.replace(' ', '_')}")
    embed.set_thumbnail(url=f"{core_url}/images/{item_name.replace(' ', '_')}.png")
    embed.add_field(name="price", value='{:,}'.format(output[item_name]['price']), inline=True)
    embed.add_field(name="volume", value=output[item_name]['volume'], inline=True)
    return embed

class GrandExchange(commands.Cog):
    """Provides user with RS3 and OSRS Grand Exchange info"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['rspc'])
    async def rsge(self, context):
        """Search RS3 GE"""
        item_request = context.message.content.split(" ", 1)[1]
        await search_grandexchange(context, 'rs', item_request)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['07ge', 'ospc', '07pc'])
    async def osge(self, context):
        """Search OSRS GE"""
        item_request = context.message.content.split(" ", 1)[1]
        await search_grandexchange(context, 'osrs', item_request)


def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(GrandExchange(bot))
