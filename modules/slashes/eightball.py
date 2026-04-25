"""Magic 8ball slash command"""
import random
import discord
from discord import app_commands
from discord.ext import commands
from utils import timestamp


EIGHTBALL_RESPONSES = [
    'It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely',
    'You may rely on it', 'As I see it, yes', 'Most likely', 'Outlook good',
    'Yes', 'Signs point to yes', 'Reply hazy try again', 'Ask again later',
    'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
    "Don't count on it", 'My reply is no', 'My sources say no', 'Outlook not so good',
    'Very doubtful',
]


class EightBallSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="8ball", description="Ask the magic 8ball anything")
    @app_commands.describe(question="The question you want to ask")
    async def eightball(self, interaction: discord.Interaction, question: str):
        """Ask the magic 8ball any question"""
        print(f"{timestamp()}: (8ball): {interaction.user} asked {question}")
        response = f"Question: {question}\n\U0001f3b1 {random.choice(EIGHTBALL_RESPONSES)} \U0001f3b1"
        await interaction.response.send_message(response)


async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(EightBallSlash(bot))
