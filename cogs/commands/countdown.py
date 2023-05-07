"""Countdown to various upcoming events"""
import re
from datetime import datetime
import pytz
from discord.ext import commands
from scripts.countdown import ufc_countdown, f1_countdown
from scripts.mma.events import gather_all_upcoming_cards

from config import timestamp as TIME

class CountdownCmd(commands.Cog):
    """How long until x happens. Requires UNIX timestamp, rest is just making it pretty"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['time', 'countdown', 'event', 'events'])
    async def when(self, context):
        """Core command to decide which event info to gather"""
        message = context.message.content.split(" ", 1)[1].lower()

        if message in ['ufc', 'mma']:
            main_output, prelim_output = ufc_countdown()
            event_title = gather_all_upcoming_cards(schedule=True)[0]
            output = f"**{event_title}**\n{main_output}\n**Prelims**\n{prelim_output}"
            await context.send(output)

        elif message in ['f1', 'motor']:
            output = f1_countdown()
            await context.send(f"**{output[0]}**\nStarts in: {output[1]}")

        elif re.match(r'^raq(|uel)?$', message):
            tz = pytz.timezone('Europe/Stockholm')
            when = datetime.now(tz)
            time_and_day = when.strftime("%H:%M:%S on %A")
            await context.send(f"It is currently {time_and_day} for raquel")
        
        else:
            await context.send("Feature not added")

        return print(f"{TIME()} {context.author} requested the next {message.upper()} event")

async def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    await bot.add_cog(CountdownCmd(bot))