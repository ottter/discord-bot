"""What the Wordle cogs share: storage, the board tables, and playing a game.

Playing is CPU work, a second or two, so it runs off the event loop. The
board tables take about a minute to build, once.
"""
import asyncio
from collections import defaultdict
from zoneinfo import ZoneInfo

from modules.wordle import answers
from modules.wordle.boards import Clues
from modules.wordle.solver import (Solver, discount, load_past, load_used, load_words,
                                   play_out, solved)

EMOJI = {'G': '🟩', 'Y': '🟨', 'B': '⬛'}
# Boards a game needs before the bot plays and locks in its result.
BOARDS_NEEDED = 3
# Where "today" is worked out when no image says otherwise.
GAME_TZ = 'America/New_York'


class Games:
    """One per bot, handed to both cogs."""

    def __init__(self, db, tz=GAME_TZ, needed=BOARDS_NEEDED):
        self.db = db
        self.tz = ZoneInfo(tz)
        self.needed = needed
        self.building = None
        # One solve at a time per guild and game, so a burst of edits can't
        # lock in two results.
        self.locks = defaultdict(asyncio.Lock)

    def start_building(self) -> None:
        """Build the board tables in the background, if not already."""
        if self.building is None:
            self.building = asyncio.ensure_future(asyncio.to_thread(Clues))

    def today(self, guild_id) -> int:
        """Today's game: by the date, or a newer number an image has shown,
        since players ahead of our timezone start the next game first."""
        return max(answers.current_game(self.tz), self.db.latest_game(guild_id) or 0)

    async def answer(self, game):
        """The game's answer, looked up once when its number is first seen."""
        word = self.db.answer(game)
        if word is None:
            word = await answers.fetch(game)
            if word:
                self.db.save_answer(game, word)
        return word

    def used_before(self, game):
        """Past answers as they stood on this game's day: past.txt, plus
        answers the bot stored for earlier games that past.txt doesn't have."""
        past = load_past()
        used = load_used(before=game, past=past)
        listed = {number for number, _ in past if number is not None}
        for number, word in self.db.answers_before(game):
            if number not in listed:
                used[word] += 1
        return used

    async def play(self, game, answer, boards):
        """Play a game with other players' boards. The turns it took."""
        clues = None
        if boards:
            self.start_building()
            clues = await self.building

        def work():
            weights = discount(load_words(), self.used_before(game))
            if clues:
                weights = clues.adjust(weights, boards)
            return play_out(answer, Solver(weights))
        return await asyncio.to_thread(work)

    async def simulate(self, word):
        """Play a word with no boards, as if it were today's answer."""
        def work():
            used = load_used()
            if used[word]:
                used[word] -= 1
            return play_out(word, Solver(discount(load_words(), used)))
        return await asyncio.to_thread(work)


def squares(pattern) -> str:
    """'BYBGB' as colored squares."""
    return ''.join(EMOJI[color] for color in pattern)


def grid(turns) -> str:
    """The colored squares, one row per guess."""
    return '\n'.join(squares(pattern) for _, pattern in turns)


def board(turns, hidden=False) -> str:
    """The squares with each guess beside its row, spoilered if hidden."""
    tag = '||' if hidden else ''
    return '\n'.join(f'{squares(pattern)} {tag}{guess}{tag}' for guess, pattern in turns)


def headline(game, turns) -> str:
    """'Wordle 1,938 3/6*' like a share; the * is hard mode. X/6* if it
    didn't solve in six."""
    score = f'{len(turns)}/6' if solved(turns) and len(turns) <= 6 else 'X/6'
    return f'Wordle {game:,} {score}*'


def spoilers(turns, answer) -> str:
    """The board with every guess, then the answer, all spoilered."""
    return f'{board(turns, hidden=True)}\nAnswer: ||{answer.upper()}||'
