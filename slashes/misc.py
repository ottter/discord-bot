"""Meme SLASH commands go here"""
from discord.ext.commands import Cog
from discord_slash import cog_ext, SlashContext

from random import choice
from config import TIME

eightball_responses = [
            'It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely',
            'You may rely on it', 'As I see it, yes', 'Most likely', 'Outlook good',
            'Yes', 'Signs point to yes', 'Reply hazy try again', 'Ask again later',
            'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
            'Don\'t count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
            'Very doubtful']

class SlashMemes(Cog):
    """All slash commands.
    Bot MUST be invited with 'applications.commands' permission for use"""

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="8ball",
        description="Ask the magic 8ball any question")
    async def _eight_ball(self, context:SlashContext):
        """Ask the magic 8ball any question"""
        print(f"{TIME}: {context.author} received their fortune (8ball)")
        await context.send(f"🎱 {choice(eightball_responses)}, <@{context.author.id}> 🎱")

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(SlashMemes(bot))
