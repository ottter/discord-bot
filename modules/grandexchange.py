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

def search_grandexchange(item):
    print(import_item(item))

class GrandExchange(commands.Cog):
    """Provides user with random and relevant xkcd comics"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def rsge(self, context):
        return search_grandexchange('rs', 'cannonball')

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['07ge'])
    async def osge(self, context):
        return search_grandexchange('osrs', 'cannonball')


def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(GrandExchange(bot))
