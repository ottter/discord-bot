from discord.ext.commands import Bot, Cog
from discord_slash import cog_ext, SlashCommand, SlashContext

class SlashOkbuddy(Cog):

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="okbuddy", 
        description="Jokes on them, I was only pretending")
    async def _okbuddy(self, context:SlashContext):
        only_pretending='https://i.imgur.com/6kGliTj.jpeg'
        await context.send(only_pretending)

def setup(bot):
    bot.add_cog(SlashOkbuddy(bot))