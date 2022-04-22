from discord.ext.commands import Bot, Cog
from discord_slash import cog_ext, SlashCommand, SlashContext

pasta_co2 = """Also CO2 is good for plants, meaning more CO2 means more life-sustaining 
oxygen and thus increase in agriculture as plants grow faster, more food, etc."""

pasta_fbi = """I DECLARE THAT EVERY POST I HAVE EVER MADE ON THIS DISCORD IS SATIRE. 
I DO NOT CONDONE NOR SUPPORT ANY OF THE OPINIONS EXPRESSED ON THIS CHATROOM."""

class SlashMemes(Cog):

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="okbuddy",
        description="Jokes on them, I was only pretending")
    async def _okbuddy(self, context:SlashContext):
        only_pretending='https://i.imgur.com/6kGliTj.jpeg'
        await context.send(only_pretending)

    @cog_ext.cog_slash(
        name="co2",
        description="promoting environmentalism")
    async def _co2(self, context:SlashContext):
        await context.send(pasta_co2)

    @cog_ext.cog_slash(
        name="fbi",
        description="posting disclaimer")
    async def _fbi(self, context:SlashContext):
        await context.send(pasta_fbi)

def setup(bot):
    bot.add_cog(SlashMemes(bot))