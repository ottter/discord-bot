"""Gather current GE price of Runescape (3 & Old School) items"""
import discord
from discord.ext import commands
import requests
import config

# https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Usage_and_APIs

def import_osrs_items():
    url = "https://chisel.weirdgloop.org/gazproj/gazbot/rs_dump.json"
    headers = {
        'User-Agent': 'github/ottter-discord-bot' }     # Owners of API request for a custom user-agent
    response = requests.get(url=url, headers=headers)
    print(f'RS Wiki Status: {response.status_code}')    # Good = 200

def search_osrs_items(item):
    import_osrs_items()

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
        return search_osrs_items('cannonball')


def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(GrandExchange(bot))
