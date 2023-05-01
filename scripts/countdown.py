"""Countdown to various upcoming events"""
import datetime
import time
import re
from bs4 import BeautifulSoup
import requests
from scripts.mma.events import build_next_card_url

HEADERS = {
    'User-Agent': 'goofcon 3'
    }

def unix_readable(unix_time):
    """Convert UNIX time into something more readable"""
    convert_time = datetime.datetime.fromtimestamp(unix_time)
    timestamp = convert_time.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp

def time_difference(event_time, timeline="future"):
    """Input UNIX time of an event and get time since/until it happens"""
    current_time = int(time.time())
    dt1 = datetime.datetime.fromtimestamp(current_time)
    dt2 = datetime.datetime.fromtimestamp(event_time)

    time_diff = dt2 - dt1
    if timeline == 'past':
        time_diff = dt1 - dt2

    total_seconds = int(time_diff.total_seconds())
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
    """Return the next F1 race, including location"""
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