""""""
from modules.ufc_data.events import build_next_card_url, gather_all_upcoming_cards
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
import datetime
import time
import re

HEADERS = {
    'User-Agent': 'goofcon 3'
    }

def unix_readable(unix_time):
    """Convert UNIX time into something more readable"""
    dt = datetime.datetime.fromtimestamp(unix_time)
    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp

def time_difference(event_time, timeline="future"):
    """Input UNIX time of an event and get time since/until it happens"""
    current_time = int(time.time())
    dt1 = datetime.datetime.fromtimestamp(current_time)
    dt2 = datetime.datetime.fromtimestamp(event_time)

    time_difference = dt2 - dt1
    if timeline == 'past':
        time_difference = dt1 - dt2

    total_seconds = int(time_difference.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60

    countdown = f"Starts in: {days} days, {hours} hours, {minutes} minutes"
    if '-' in countdown:
        countdown = "Looks like it already passed"
    return countdown

def ufc_countdown():
    """Gather the UNIX timestamp of the next UFC event using modules/ufc_data/events.py"""
    if build_next_card_url(0).status_code != 200:
        return print("Can't access website right now. Try again later")
    soup = BeautifulSoup(build_next_card_url(0).content, features="html.parser")
    timestamp = soup.find_all('div', {'class': 'c-event-fight-card-broadcaster__time'})
    main_output = time_difference(int(timestamp[0]['data-timestamp']))
    prelim_output = time_difference(int(timestamp[1]['data-timestamp']))
    return main_output, prelim_output

def f1_countdown():
    """"""
    f1_request = requests.get('https://lightsouts.com/formula-1', headers = HEADERS)
    if f1_request.status_code != 200:
        return print("Can't access website right now. Try again later")
    time_until = []
    soup = BeautifulSoup(f1_request.content, features="html.parser")
    next_f1 = soup.find_all('div', {'tabindex': '-1'})
    for item in next_f1:
        # Page has attribute 'data-unit' with values equally which time unit
        unit = item.find_all('div', {'data-unit': re.compile(r'days|hours|minutes|seconds')})
        for content in unit:
            # Remove letters from the text (ie: days, hours, minutes, seconds)
            time_until.append(re.sub(r'\D', '', content.text))
    race_loc = [x.find('h2').text for x in next_f1][0]
    time_str = f"{time_until[0]} days, {time_until[1]} hours, {time_until[2]} minutes"
    return race_loc, time_str

class Countdown(commands.Cog):
    """How long until x happens. Requires UNIX timestamp, rest is just making it pretty"""
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['time', 'countdown', 'event', 'events'])
    async def when(self, context):
        message = context.message.content.split(" ", 1)[1].lower()

        if message in ['ufc', 'mma']:
            main_output, prelim_output = ufc_countdown()
            event_title = gather_all_upcoming_cards(schedule=True)[0]
            output = f"**{event_title}**\n{main_output}\n**Prelims**\n{prelim_output}"
            return await context.send(output)
        
        if message == 'f1':
            output = f1_countdown()
            return await context.send(f"**{output[0]}**\nStarts in: {output[1]}")
        
        else:
            return await context.send("Feature not added")

def setup(bot):
    """Adds the cog (module) to startup. See main/load_extensions"""
    bot.add_cog(Countdown(bot))