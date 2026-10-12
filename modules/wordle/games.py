"""What the Wordle cogs share: storage, the board tables, and playing a game.

Playing is CPU work, a second or two, so it runs off the event loop. The
board tables take about a minute to build, once.
"""
import asyncio
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

from modules.wordle import answers
from modules.wordle.boards import Clues
from modules.wordle.solver import (DATA, GUESSES, OPENER, Solver, discount, load_past, load_used,
                                   load_words, play_out, solved)

EMOJI = {'G': '🟩', 'Y': '🟨', 'B': '⬛'}
# Boards a game needs before the bot plays and locks in its result.
BOARDS_NEEDED = 3
# Where "today" is worked out when no image says otherwise.
GAME_TZ = 'America/New_York'
# Work the opener out from other boards instead of always slate. Over 15 real
# days it averaged 2.47 guesses against slate's 2.60 (4 better, 2 worse).
PICK_OPENER = True


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
        self.version = solver_version()
        self.db.prune_plays(self.version)

    def start_building(self) -> None:
        """Build the board tables in the background, if not already."""
        if self.building is None:
            self.building = asyncio.ensure_future(asyncio.to_thread(Clues))

    def today(self, guild_id) -> int:
        """Today's game: by the date, or a newer number an image has shown,
        since players ahead of our timezone start the next game first."""
        return max(answers.current_game(self.tz), self.db.latest_game(guild_id) or 0)

    def newest(self, guild_id) -> int:
        """The newest game that can be played: today's, or a newer one any
        Wordle post has shown. NYT publishes answers ahead, so nothing past
        this is played."""
        return max(self.today(guild_id), self.db.latest_game() or 0)

    async def answer(self, game, keep=True):
        """The game's answer, looked up once when its number is first seen.
        Replays don't keep theirs, so the stored ones are all days the bot
        played as they happened."""
        word = self.db.answer(game)
        if word is None:
            word = await answers.fetch(game)
            if word and keep:
                self.db.save_answer(game, word)
        return word

    def used_before(self, game, replay=None):
        """Past answers as they stood on this game's day: past.txt, plus
        answers the bot stored for earlier games that past.txt doesn't have.

        A replay's answer is passed as `replay`. For a game from before the
        bot started, past.txt has no dates and already holds that game's own
        answer, so that one use is set aside."""
        past = load_past()
        used = load_used(before=game, past=past)
        listed = {number for number, _ in past if number is not None}
        for number, word in self.db.answers_before(game):
            if number not in listed:
                used[word] += 1
        first = self.db.first_answer()
        if replay and (first is None or game < first) and used[replay]:
            used[replay] -= 1
        return used

    async def play(self, game, answer, boards, replay=False):
        """Play a game with other players' boards. The turns it took.

        The same game, boards and solver always play the same way, so each
        play is saved and only worked out once."""
        key = (game, digest(boards), replay, self.version)
        turns = self.db.cached_play(key)
        if turns is None:
            # Through JSON, so a fresh play looks the same as a saved one.
            turns = json.loads(json.dumps(await self.work_out(game, answer, boards, replay)))
            self.db.cache_play(key, turns)
        return turns

    async def blind(self, game, answer, replay=False):
        """The same game with no boards at all, to show what they were worth."""
        return await self.play(game, answer, [], replay)

    async def work_out(self, game, answer, boards, replay):
        """Actually play the game, off the event loop."""
        clues = None
        if boards:
            self.start_building()
            clues = await self.building

        def work():
            weights = discount(load_words(),
                               self.used_before(game, answer if replay else None))
            if clues:
                weights = clues.adjust(weights, boards)
            opener = None if clues and PICK_OPENER else OPENER
            return play_out(answer, Solver(weights, opener=opener))
        return await asyncio.to_thread(work)

    async def simulate(self, word):
        """Play a word with no boards, as if it were today's answer."""
        def work():
            used = load_used()
            if used[word]:
                used[word] -= 1
            return play_out(word, Solver(discount(load_words(), used)))
        return await asyncio.to_thread(work)


def digest(boards) -> str:
    """A fingerprint of a set of boards, in any order."""
    text = json.dumps(sorted(boards))
    return hashlib.sha1(text.encode()).hexdigest()


def solver_version() -> str:
    """A fingerprint of the code and word lists a play depends on, so saved
    plays are dropped once any of them change."""
    here = Path(__file__).parent
    files = [here / 'solver.py', here / 'boards.py', here / 'games.py',
             *sorted(DATA.glob('*.txt'))]
    hashed = hashlib.sha1()
    for path in files:
        hashed.update(path.read_bytes())
    return hashed.hexdigest()[:12]


def squares(pattern) -> str:
    """'BYBGB' as colored squares."""
    return ''.join(EMOJI[color] for color in pattern)


def grid(turns) -> str:
    """The colored squares, one row per guess."""
    return '\n'.join(squares(turn[1]) for turn in turns)


def board(turns) -> str:
    """The squares with each guess beside its row."""
    return '\n'.join(f'{squares(turn[1])} {turn[0]}' for turn in turns)


def blind_note(blind) -> str:
    """What a play with no boards, from the opener, scored."""
    return f"Starting blind with {OPENER.upper()}, I'd have gotten {tally(blind)}."


def official_note(turns, boards) -> str:
    """The locked-in result, for when a play has used more boards than it."""
    return f'My official score is {tally(turns)} using {boards_text(boards)}.'


def boards_text(boards) -> str:
    """'1 board' or '3 boards'."""
    return f'{boards} board{"" if boards == 1 else "s"}'


def guesses_taken(turns) -> int:
    """Guesses taken, with a miss counted as one more than the limit."""
    return len(turns) if solved(turns) and len(turns) <= GUESSES else GUESSES + 1


def tally(turns) -> str:
    """'3/6', or 'X/6' if it didn't solve in six."""
    taken = guesses_taken(turns)
    return f'{taken if taken <= GUESSES else "X"}/{GUESSES}'


def headline(game, turns) -> str:
    """'Wordle 1,938 3/6*' like a share; the * is hard mode."""
    return f'Wordle {game:,} {tally(turns)}*'


def spoilers(turns, answer, boards) -> str:
    """The board with each guess in bold capitals and the words it was picked
    over in italics, each with how likely it looked to be the answer, then the
    answer and how many boards it was played from, all spoilered. Results
    saved before these were kept show just the guess."""
    rows = []
    for turn in turns:
        options = turn[2] if len(turn) > 2 else [[turn[0], None]]
        picked, *others = [labelled(word, chance, bold=i == 0)
                           for i, (word, chance) in enumerate(options)]
        rest = f' ({", ".join(others)})' if others else ''
        rows.append(f'{squares(turn[1])} ||{picked}{rest}||')
    return '\n'.join(rows + [f'Answer from {boards_text(boards)}: ||{answer.upper()}||'])


def labelled(word, chance, bold) -> str:
    """A word in bold or italics with its chance. Words already ruled out as
    the answer, played only to narrow things down, get no number."""
    text = f'**{word.upper()}**' if bold else f'*{word}*'
    if chance is None:
        return text
    return f'{text} {"<1%" if chance < 0.01 else f"{chance:.0%}"}'
