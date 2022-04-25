"""Guild Event related Discord functions"""
from discord.ext import commands


class GuildEvents(commands.Cog):
    """Class holding guild events (leave, join, etc)"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Actions upon joining a new server"""
        # with open('./files/prefix.json', 'r') as file:
        #     prefixes = json.load(file)
        # prefixes[str(guild.id)] = "."
        # with open('./files/prefix.json', 'w') as file:
        #     json.dump(prefixes, file, indent=4)
        print(f'joined new server: {guild}')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Actions upon leaving a server"""
        # Removes the custom prefix from prefixes.json when bot is removed from a server
        # with open('./files/prefix.json', 'r') as file:
        #     prefixes = json.load(file)
        # prefixes.pop(str(guild.id))
        # with open('./files/prefix.json', 'w') as file:
        #     json.dump(prefixes, file, indent=4)
        print(f'left server: {guild}')

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(GuildEvents(bot))
