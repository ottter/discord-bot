"""Gather info about the UFC. Events, Matchups, Fighters, etc"""
import re
import discord
from modules.ufc_data.events import *
from modules.ufc_data.odds import *
from modules.ufc_data.rankings import *
from modules.ufc_data.fighters import *
from discord.ext import commands

def ufc_data(context, message):
    """Read the user input to determine which data to fetch"""
    category, argument = message.split(" ", 1)[0], message.split(" ", 1)[1]
    arguments = argument.split()

    if re.compile(r"\bevents?\b").match(category):      # Category: Events
        matchups = get_event(card=arguments[0], format=arguments[1], next_event=0)
        odds = create_odds_matchups(card=arguments[0], mark_favorite=True, next_event=0)
        output = [l1 + "\t\t|  " + l2 for (l1, l2) in zip(matchups, odds)]
        output = "\n".join(output)
        return context.send(output)
    else:
        return context.send('TBD')

class UltimateFighing(commands.Cog):
    """Provides user with UFC info"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def ufc(self, context):
        try:
            message = context.message.content.split(" ", 1)[1].lower()
        except:
            # If no argument is passed, then default to getting info on next event
            message = 'event main matchups 0'
        await ufc_data(context, message)

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(UltimateFighing(bot))
