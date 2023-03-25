from modules.ufc_data.events import build_next_card_url, gather_all_upcoming_cards
from discord.ext import commands
from bs4 import BeautifulSoup
import datetime
import time

HEADERS = {
    'User-Agent': 'goofcon 3'
    }

def unix_readable(unix_time):
    dt = datetime.datetime.fromtimestamp(unix_time)
    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp

def time_difference(event_time):
    """Input UNIX time and get returned time until that event"""
    current_time = int(time.time())
    dt1 = datetime.datetime.fromtimestamp(current_time)
    dt2 = datetime.datetime.fromtimestamp(event_time)
    time_difference = dt2 - dt1

    total_seconds = int(time_difference.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60

    countdown = f"{days} days, {hours} hours, {minutes} minutes"
    if '-' in countdown:
        countdown = "Looks like it already passed"
    return countdown

def ufc_countdown():
    soup = BeautifulSoup(build_next_card_url(0).content, features="html.parser")
    timestamp = soup.find_all('div', {'class': 'c-event-fight-card-broadcaster__time'})
    main_output = time_difference(int(timestamp[0]['data-timestamp']))
    prelim_output = time_difference(int(timestamp[1]['data-timestamp']))
    return main_output, prelim_output

class Countdown(commands.Cog):
    """How long until x"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['time', 'countdown', 'event', 'events'])
    async def when(self, context):
        message = context.message.content.split(" ", 1)[1].lower()
        if message == 'ufc':
            main_output, prelim_output = ufc_countdown()
            event_title = gather_all_upcoming_cards(schedule=True)[0]
            output = f"**{event_title}**\n{main_output}\n**Prelims**\n{prelim_output}"
            await context.send(output)
        else:
            await context.send("Feature not added")

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(Countdown(bot))