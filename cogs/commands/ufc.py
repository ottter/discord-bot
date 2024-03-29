"""Gather info about the UFC. Events, Matchups, Fighters, etc"""
import re
from config import timestamp as TIME
from scripts.mma.events import get_event
from scripts.mma.odds import create_odds_matchups
from scripts.mma.rankings import weightclass_rankings
from discord.ext import commands

def ufc_data(context, message):
    """Read the user input to determine which data to fetch
       Desired input will be something like: .ufc {category} {argument}"""

    category, argument = message.split(" ", 1)[0], message.split(" ", 1)[1]
    arguments = argument.split()

    # Category: Event(s)
    # Match:    event, events
    if re.compile(r"\bevents?\b").match(category):
        matchups = get_event(card=arguments[0], 
                             display_format=arguments[1], 
                             next_event=0)
        odds = create_odds_matchups(card=arguments[0], 
                                    mark_favorite=True, 
                                    next_event=0)
        output = [l1 + "\t\t|  " + l2 for (l1, l2) in zip(matchups, odds)]
        output = "\n".join(output)
        return context.send(output)
    
    # Category: Weightclass
    # Match:    weightclass, class, rank, ranking, rankings
    if re.compile(r"\b(weight|)class|rank(|ings?)\b").match(category):
        # rankings = [List of fighters for x rank, Official weightclass name]
        rankings = weightclass_rankings(weightclass=arguments[0], 
                                        mark_champion=True, 
                                        numerate_fighters=True)
        rankings[0].insert(0, f"**Current {rankings[1]} Rankings**")
        output = "\n".join(rankings[0])
        return context.send(output)
    return context.send('TBD')

class UltimateFighting(commands.Cog):
    """Provides user with UFC info"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['mma'])
    async def ufc(self, context):
        """Core command for gathering UFC information"""
        accepted_subcommands = []
        try:
            # message = everything after the command
            user_input = context.message.content.split(" ", 1)[1].lower()
            if user_input.split(" ")[0] in accepted_subcommands:
                print(f'{TIME()}: {context.author} gave a valid ufc subcommand : {context.message.content}')
                message = user_input
            else: 
                # If invalid entry is given
                print(f'{TIME()}: {context.author} gave invalid ufc subcommand : {context.message.content}')
                message = 'event main matchups 0'
        except:
            # If no argument is passed, then default to getting info on next event
            print(f'{TIME()}: {context.author} requested UFC event information')
            message = 'event main matchups 0'
        await ufc_data(context, message)

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(UltimateFighting(bot))