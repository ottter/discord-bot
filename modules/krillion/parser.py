"""Parsing and day maths for krillion.io share text.

A daily share looks like:

    Krillion #66 🦐
    300

    🦑🐟🐟🐟🦑🦑🐟

Archive (⟲) and unlimited (∞) shares use the same shape but aren't the daily
puzzle, so they're parsed and then rejected by name.
"""
import datetime
import re
from zoneinfo import ZoneInfo

# krillion.io rolls over at midnight Eastern; day 1 was 2026-07-16.
GAME_TZ = ZoneInfo('America/New_York')
EPOCH = datetime.date(2026, 7, 16)
ROUNDS_PER_DAY = 7
MAX_DAY_SCORE = 700

# Tier emoji, best to worst. Only used to count rounds and render results.
TIER_EMOJI = ('🌟', '🏮', '🦑', '🐟', '🤡', '🫧', '⬛')

# 'Krillion #66 🦐' — an optional marker before the # means archive or unlimited.
# The day is capped at 6 digits so a padded number can't blow up downstream.
HEADER = re.compile(r'^Krillion\s*(?P<marker>[⟲∞])?\s*#(?P<day>\d{1,6})\b')
SCORE = re.compile(r'^(?P<score>\d{1,4})$')

MARKER_NAMES = {'⟲': 'archive', '∞': 'unlimited'}


class ParseError(Exception):
    """Share text that we understood well enough to explain the problem."""


def today_day_number(now=None) -> int:
    """Which puzzle number is live right now.

    Always answers in Eastern, so passing a UTC time gives the same day as the
    Eastern time for that instant.
    """
    now = now or datetime.datetime.now(GAME_TZ)
    return (now.astimezone(GAME_TZ).date() - EPOCH).days + 1


def date_for_day(day: int) -> datetime.date:
    """The calendar date a puzzle number fell on."""
    return EPOCH + datetime.timedelta(days=day - 1)


def parse_share(text: str) -> dict:
    """Pull day, score and tiles out of share text.

    Returns None for text that isn't a Krillion share, so ordinary chat needs
    no exception handling. Raises ParseError, with a reason worth showing the
    user, when it looks like a share but can't be used.
    """
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return None

    header = HEADER.match(lines[0])
    if not header:
        return None

    marker = header.group('marker')
    if marker:
        raise ParseError(f"that's an {MARKER_NAMES[marker]} run, not today's dive")

    if len(lines) < 3:
        raise ParseError('that looks cut off — paste the whole share, tiles included')

    score = SCORE.match(lines[1])
    if not score:
        raise ParseError('could not find the score on the second line')

    tiles = [char for char in lines[2] if char in TIER_EMOJI]
    if len(tiles) != ROUNDS_PER_DAY:
        raise ParseError(f'expected {ROUNDS_PER_DAY} tiles, counted {len(tiles)}')

    score = int(score.group('score'))
    if score > MAX_DAY_SCORE:
        raise ParseError(f'{score} is above the {MAX_DAY_SCORE} daily maximum')

    return {'day': int(header.group('day')), 'score': score, 'emoji': ''.join(tiles)}
