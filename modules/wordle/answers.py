"""Look up a game's answer from NYT by its number.

Wordle numbers count days since launch (#0 was 2021-06-19), and NYT serves
each day's answer by date. The bot only asks once per game, when its number
first shows up in an image. The answer is never given to the solver; it only
colors the bot's guesses, the way the game would.
"""
import asyncio
import datetime
import logging

import aiohttp

log = logging.getLogger('discord.bot')

LAUNCH = datetime.date(2021, 6, 19)
URL = 'https://www.nytimes.com/svc/wordle/v2/{}.json'


def date_for(game: int) -> datetime.date:
    """The date a game number was played on."""
    return LAUNCH + datetime.timedelta(days=game)


def current_game(tz) -> int:
    """Today's game number in that timezone."""
    return (datetime.datetime.now(tz).date() - LAUNCH).days


async def fetch(game: int):
    """The game's answer, or None if NYT can't be reached."""
    url = URL.format(date_for(game).isoformat())
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20),
                                         headers={'User-Agent': 'Mozilla/5.0'}) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)
        return data['solution'].lower()
    except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, ValueError) as err:
        log.warning('Could not fetch the answer to Wordle %s: %s', game, err)
        return None
