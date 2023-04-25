"""Meme SLASH commands go here"""
import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import Cog

from random import choice
from config import TIME

eightball_responses = [
            'It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely',
            'You may rely on it', 'As I see it, yes', 'Most likely', 'Outlook good',
            'Yes', 'Signs point to yes', 'Reply hazy try again', 'Ask again later',
            'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
            'Don\'t count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
            'Very doubtful']

class EightBallSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="eightball", description="Ask the magic 8ball anything")
    async def self(interation: discord.Interaction, question:str, context:str):
        """Ask the magic 8ball any question"""
        print(f"{TIME}: (8ball) {context.author}: {question}")
        response = f"🎱 {choice(eightball_responses)} 🎱"
        await interation.response.send_message(response)

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(EightBallSlash(bot))