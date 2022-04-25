"""Meme SLASH commands go here"""
from discord.ext.commands import Cog
from discord_slash import cog_ext, SlashContext

PASTA_CO2 = ("Also CO2 is good for plants, meaning more CO2 means more life-sustaining"
    " oxygen and thus increase in agriculture as plants grow faster, more food, etc.")

PASTA_FBI = ("I DECLARE THAT EVERY POST I HAVE EVER MADE ON THIS DISCORD IS SATIRE."
    " I DO NOT CONDONE NOR SUPPORT ANY OF THE OPINIONS EXPRESSED ON THIS CHATROOM.")

slash_img_dict = {
    "only_pretending"   : "https://i.imgur.com/6kGliTj.jpeg",
    "pepe_copium"       : "https://i.imgur.com/feSABOV.jpeg",
    "pepe_bedge"        : "https://cdn.betterttv.net/emote/6049a20d306b602acc59aab5/3x",
    "no_maidens"        : "https://i.imgur.com/iqv14Bb.jpg",
}

class SlashMemes(Cog):
    """All slash commands.
    Bot MUST be invited with 'applications.commands' permission for use"""

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="okbuddy",
        description="Jokes on them, I was only pretending")
    async def _okbuddy(self, context:SlashContext):
        await context.send(slash_img_dict["only_pretending"])

    @cog_ext.cog_slash(
        name="cope",
        description="Copium OD")
    async def _copium(self, context:SlashContext):
        await context.send(slash_img_dict["pepe_copium"])

    @cog_ext.cog_slash(
        name="bedge",
        description="Go to bed")
    async def _bedge(self, context:SlashContext):
        await context.send(slash_img_dict["pepe_bedge"])

    @cog_ext.cog_slash(
        name="maidens",
        description="Maidenless Behavior")
    async def _maidens(self, context:SlashContext):
        await context.send(slash_img_dict["no_maidens"])

    @cog_ext.cog_slash(
        name="co2",
        description="promoting environmentalism")
    async def _co2(self, context:SlashContext):
        await context.send(PASTA_CO2)

    @cog_ext.cog_slash(
        name="fbi",
        description="posting disclaimer")
    async def _fbi(self, context:SlashContext):
        await context.send(PASTA_FBI)

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(SlashMemes(bot))
