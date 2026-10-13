"""Adjust answer weights using other players' boards, colors only.

Every row someone else got is a clue. A first row is a free choice, so for
each possible answer the question is how often a typical opener would show
it: a rare row like BGGGG says a lot, a common one like BBYBB barely
anything. Later guesses have to fit what the player has seen, so they aren't
free choices; for those the question is only whether some likely word could
show the row at all. Nobody is assumed to have played any particular word,
and the day's answer is never part of this.
"""
from array import array
from itertools import islice

from modules.wordle.solver import GUESSES_PATH, SOLVED, code, load_words, to_code

# How much other boards count. 0 ignores them; 1 takes every row at face value.
BOARD_TRUST = 1.0
# A first row never cuts an answer below this share of the best fit, in case
# someone opened with an odd word or a board was misread.
FLOOR = 0.02
# A later row no likely word could show only means the player guessed
# something odd, which people do, so it cuts an answer less.
LATER_FLOOR = 0.1
# Judge what players guess by how common words are, not by answer weights,
# which push plurals and past tenses like TIRED far down.
PLAIN_GUESSES = True
# Players mostly guess common words, so these are the typical guesses.
TYPICAL = 1000
# Words a player might really guess after their opener.
LIKELY = 3000
# Share of games each opener starts, from NYT's chart of 515 million games
# (Dec 2022 to Nov 2023). The other first rows are common words, like later rows.
POPULAR = {
    'adieu': 0.08, 'stare': 0.043, 'slate': 0.039, 'audio': 0.036, 'raise': 0.031,
    'crane': 0.018, 'arise': 0.017, 'irate': 0.014, 'train': 0.013, 'great': 0.009,
    'heart': 0.009, 'arose': 0.008, 'house': 0.008, 'aisle': 0.008, 'steam': 0.008,
    'least': 0.007, 'crate': 0.007, 'tears': 0.007, 'salet': 0.006, 'dream': 0.006,
}


class Clues:
    """How each answer would color the guesses players make, worked out once."""

    def __init__(self, weights=None):
        weights = weights or load_words()
        # Players guess from plain frequency; past answers don't put them off.
        guessed = load_words(GUESSES_PATH) if PLAIN_GUESSES else weights
        typical = dict(islice(guessed.items(), TYPICAL))
        # The popular openers' share of games, then the rest spread by frequency.
        scale = (1 - sum(POPULAR.values())) / sum(typical.values())
        openers = {word: weight * scale for word, weight in typical.items()}
        for word, share in POPULAR.items():
            openers[word] = openers.get(word, 0) + share
        likely = set(islice(guessed, LIKELY))

        # For each answer: the share of openers showing each pattern, indexed
        # by the pattern's number, and one bit per pattern any likely word
        # could show later on. Kept compact, since it's every word: a dict
        # and a set per answer came to about 200 MB.
        self.first_fit, self.later_fit = {}, {}
        guesses = list(dict.fromkeys([*openers, *likely]))
        # Every word, since a rare one is sometimes the answer (strew, #1937).
        for answer in weights:
            first, later = array('d', bytes(8 * (SOLVED + 1))), 0
            for guess in guesses:
                value = code(guess, answer)
                first[value] += openers.get(guess, 0)
                if guess in likely:
                    later |= 1 << value
            self.first_fit[answer], self.later_fit[answer] = first, later

    def adjust(self, weights: dict, boards: list, trust: float = None) -> dict:
        """The weights reweighed by other boards, most likely first again.

        Each board is its rows in order, like ['BBBYB', 'BGGBB', 'GGGGG'].
        """
        trust = BOARD_TRUST if trust is None else trust
        if not trust or not boards:
            return weights

        factor = self.factors(boards, trust)
        adjusted = {word: weight * factor.get(word, 1) for word, weight in weights.items()}
        # Kept on the same scale, so settings like MIN_GAIN mean the same thing.
        scale = sum(weights.values()) / sum(adjusted.values())
        return dict(sorted(((word, weight * scale) for word, weight in adjusted.items()),
                           key=lambda item: -item[1]))

    def factors(self, boards: list, trust: float) -> dict:
        """What each answer's weight gets multiplied by."""
        factor = dict.fromkeys(self.first_fit, 1.0)
        for rows in boards:
            for turn, pattern in enumerate(rows):
                value = to_code(pattern)
                if value == SOLVED:
                    break
                fit = {answer: self.fit(answer, turn, value) for answer in factor}
                best = max(fit.values())
                # No typical guess shows this for any answer: an odd word, so skip it.
                if not best:
                    continue
                floor = FLOOR if turn == 0 else LATER_FLOOR
                for answer in factor:
                    factor[answer] *= (max(fit[answer], floor * best) / best) ** trust
        return factor

    def fit(self, answer: str, turn: int, value: int) -> float:
        """How well this answer explains a row, before the floor and trust."""
        if turn == 0:
            return self.first_fit[answer][value]
        return float(self.later_fit[answer] >> value & 1)
