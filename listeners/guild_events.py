import json
from discord.ext import commands

class GuildEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(guild):
        # with open('./files/prefix.json', 'r') as file:
        #     prefixes = json.load(file)
        # prefixes[str(guild.id)] = "."
        # with open('./files/prefix.json', 'w') as file:
        #     json.dump(prefixes, file, indent=4)
        print(f'joined new server: {guild}')

    @commands.Cog.listener()
    async def on_guild_remove(guild):
        # Removes the custom prefix from prefixes.json when bot is removed from a server
        # with open('./files/prefix.json', 'r') as file:
        #     prefixes = json.load(file)
        # prefixes.pop(str(guild.id))
        # with open('./files/prefix.json', 'w') as file:
        #     json.dump(prefixes, file, indent=4)
        print(f'left server: {guild}')

def setup(bot):
    bot.add_cog(GuildEvents(bot))
