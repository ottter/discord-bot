"""Suggests guesses from the colors seen so far.

Started from https://github.com/ottter/wordle-loser. data/words.txt is every
allowed word with a weight, roughly its chance of being the answer; see
tools/sort_words.py. Patterns are five of G (green), Y (yellow) and B (gray).
"""
import math
from collections import Counter
from itertools import islice
from pathlib import Path

DATA = Path(__file__).parent / 'data'
WORDS_PATH = DATA / 'words.txt'
# Every answer so far, repeats included. Lines are a word, or a game number
# and its word (`1938 major`) for ones added by hand; the bot stores the rest.
PAST_PATH = DATA / 'past.txt'
VOWELS = set('aeiou')
# Place values of the five squares in a pattern's number, see code().
PLACES = (1, 3, 9, 27, 81)
SOLVED = 242

# Best of eight popular openers in hard mode, and of its own anagrams.
OPENER = 'slate'
# Guesses are only drawn from the most common words, which keeps a suggestion
# quick and stops it playing words nobody knows.
GUESS_POOL = 3000
# Likely answers past this many barely move the expected outcome.
SAMPLE = 300
GUESSES = 6
# Guess the likeliest word outright once it holds this share of the weight left.
SURE = 0.5
# How many likely words left over one lost game is worth, when weighing a
# guess's split against its traps in hard mode. 0 turns the check off.
LOSS_COST = 20
# How many of the best splitting guesses get checked for traps.
SHORTLIST = 100
# Guesses scoring within this fraction of the best count as tied, and a tied
# word at least MIN_GAIN likelier to be the answer is played instead.
NEAR_TIE = 0.1
MIN_GAIN = 0.1
# Whether guessing the answer counts as leaving nothing, see expected_left.
SOLVED_LEAVES_NOTHING = True
# Share of its weight a past answer keeps, see discount(). About 1 game in 10
# has repeated since reuse began on 2 Feb 2026, and that's expected to rise.
# 0.2 holds up best from 10% to 25% repeats; heavier cuts lose on repeat days.
USED_FACTOR = 0.2
# Judge splits by entropy (information gained) instead of expected weight left.
ENTROPY = False


def load_words(path=WORDS_PATH) -> dict:
    """Word to weight, most likely first."""
    pairs = (line.split() for line in path.read_text(encoding='utf-8').splitlines())
    return {word: float(weight) for word, weight in pairs}


def load_past(path=PAST_PATH) -> list:
    """(game number or None, word) for every line of past.txt, in order."""
    games = []
    for line in path.read_text(encoding='utf-8').splitlines():
        parts = line.split()
        if parts:
            games.append((int(parts[0]) if len(parts) == 2 else None, parts[-1]))
    return games


def load_used(before=None, past=None) -> Counter:
    """How many times each word has been the answer.

    Numbered games from `before` on are left out, so a game is played as it was
    on its day. Pass `past` from load_past() to save reading the file again.
    """
    return Counter(word for number, word in (past or load_past())
                   if before is None or number is None or number < before)


def discount(weights: dict, used: Counter, factor: float = None) -> dict:
    """The weights with past answers cut down, most likely first again.

    A used word is less likely than an unused one as common, but still well
    above words nobody knows. Each use cuts it again, so a word used twice
    keeps factor squared.
    """
    factor = USED_FACTOR if factor is None else factor
    cut = {word: weight * factor ** used[word] for word, weight in weights.items()}
    return dict(sorted(cut.items(), key=lambda item: -item[1]))


def code(guess: str, answer: str) -> int:
    """The pattern Wordle shows for a guess, as a number from 0 to 242.

    Each square is a base 3 digit, gray 0, yellow 1, green 2, first square
    lowest. Greens are taken first, so a repeated letter only turns yellow
    while the answer still has a spare one.
    """
    # Called millions of times per suggestion, so kept to plain lists.
    value = 0
    spare = []
    misses = []
    for i in range(5):
        if guess[i] == answer[i]:
            value += 2 * PLACES[i]
        else:
            spare.append(answer[i])
            misses.append(i)

    for i in misses:
        if guess[i] in spare:
            value += PLACES[i]
            spare.remove(guess[i])
    return value


def to_code(pattern: str) -> int:
    """'BYBGB' to its number."""
    return sum('BYG'.index(color) * place for color, place in zip(pattern, PLACES))


def to_pattern(value: int) -> str:
    """A pattern's number back to letters like 'BYBGB'."""
    return ''.join('BYG'[value // place % 3] for place in PLACES)


def score(guess: str, answer: str) -> str:
    """The pattern Wordle shows for a guess, as letters like 'BYBGB'."""
    return to_pattern(code(guess, answer))


def unique_vowels(word: str) -> int:
    """Getting the vowels out early opens up the board."""
    count = len(VOWELS & set(word))
    return count if count >= 2 else 0


def play_out(answer: str, solver, limit: int = GUESSES) -> list:
    """(guess, pattern) for each turn, stopping when solved or out of turns.

    The answer only colors the solver's own guesses, as the game would.
    """
    turns = []
    while len(turns) < limit:
        guess = solver.suggest()
        if guess is None:
            break
        pattern = score(guess, answer)
        turns.append((guess, pattern))
        if pattern == 'GGGGG':
            break
        solver.add(guess, pattern)
    return turns


def solved(turns) -> bool:
    """Whether the last turn was the answer."""
    return bool(turns) and turns[-1][1] == 'GGGGG'


class Solver:
    """One game's guesses and the words still possible."""

    def __init__(self, weights, opener=OPENER, vowels=False, hard=True):
        self.weights = weights
        self.candidates = list(self.weights)
        self.opener = opener
        # wordle-loser's rule, kept to compare against.
        self.vowels = vowels
        self.hard = hard
        self.history = []
        # Patterns the trap check has worked out, keyed by guess + answer. It
        # asks for the same few thousand pairs again; caching the bigger
        # splits too cost ~100 MB a game for little speed.
        self.seen = {}

    def add(self, guess: str, pattern: str) -> None:
        """Keep only the words that would have shown this pattern."""
        guess, pattern = guess.lower(), pattern.upper()
        if len(guess) != 5 or len(pattern) != 5 or set(pattern) - set('GYB'):
            raise ValueError(f'expected a 5 letter word and pattern, got {guess} {pattern}')

        self.history.append((guess, pattern))
        target = to_code(pattern)
        self.candidates = [word for word in self.candidates
                           if code(guess, word) == target]

    def pattern(self, guess: str, answer: str) -> int:
        """code(), remembered for this game."""
        key = guess + answer
        value = self.seen.get(key)
        if value is None:
            value = self.seen[key] = code(guess, answer)
        return value

    def suggest(self) -> str:
        """Next guess, or None if the patterns rule everything out."""
        if not self.candidates:
            return None
        if not self.history:
            return self.opener
        if self.vowels:
            # max keeps the first of equals, so the likeliest wins ties.
            return max(self.candidates, key=unique_vowels)

        likeliest = self.candidates[0]
        total = sum(self.weights[word] for word in self.candidates)
        if len(self.history) >= GUESSES - 1:
            return likeliest
        if self.weights[likeliest] >= total * SURE:
            return likeliest

        sample = self.candidates[:SAMPLE]
        possible = set(self.candidates)
        # Candidates always pass hard mode, so there's always something to pick.
        # The likeliest answers are usually in the pool too, so drop repeats.
        pool = list(islice(self.weights, GUESS_POOL))
        guesses = [word for word in dict.fromkeys(pool + sample) if self.allowed(word)]

        cost = {guess: self.expected_left(guess, sample) for guess in guesses}
        if self.hard and LOSS_COST:
            # Only the best splitters are worth the slower trap check.
            cost = {guess: cost[guess] + LOSS_COST * self.trap_loss(guess, sample)
                    for guess in sorted(guesses, key=cost.get)[:SHORTLIST]}

        def win(guess):
            return self.weights[guess] if guess in possible else 0

        best = min(cost, key=lambda guess: (cost[guess], guess not in possible))
        # When splits are near equal, a guess that could win now beats a probe,
        # but only if it's clearly likelier than the best splitter.
        close = [guess for guess in cost if cost[guess] <= cost[best] * (1 + NEAR_TIE)]
        bet = max(close, key=win)
        return bet if win(bet) - win(best) >= MIN_GAIN else best

    def trap_loss(self, guess: str, answers: list) -> float:
        """Weight of answers this guess would likely lose to traps.

        A trap is a group of words the same but for one letter, like _ATCH.
        Hard mode keeps the four letters, so each guess only rules out one
        word, and any past the guesses left are lost. Each color pattern
        counts its worst trap.
        """
        left = GUESSES - len(self.history) - 1
        groups = {}
        for answer in answers:
            groups.setdefault(self.pattern(guess, answer), []).append(answer)
        groups.pop(SOLVED, None)

        lost = 0
        for words in groups.values():
            traps = {}
            for word in words:
                for i in range(5):
                    traps.setdefault(word[:i] + '_' + word[i + 1:], []).append(self.weights[word])
            # The likeliest get tried first, so the rarest are the ones lost.
            lost += max(sum(sorted(trap, reverse=True)[left:]) for trap in traps.values())
        return lost

    def allowed(self, guess: str) -> bool:
        """Whether hard mode lets you play this.

        Greens stay where they are, and yellows can go anywhere but can't be
        left out.
        """
        if not self.hard:
            return True
        for played, pattern in self.history:
            found = Counter()
            for i, (letter, color) in enumerate(zip(played, pattern)):
                if color == 'G' and guess[i] != letter:
                    return False
                if color != 'B':
                    found[letter] += 1
            if any(guess.count(letter) < count for letter, count in found.items()):
                return False
        return True

    def expected_left(self, guess: str, answers: list) -> float:
        """Weight of answers still possible after this guess, on average.

        Smaller means the colors it shows would split the answers better.
        Guessing the answer leaves nothing to find, which favors likely
        answers by how likely they are.
        """
        groups = self.groups(guess, answers)
        total = sum(groups.values())
        if SOLVED_LEAVES_NOTHING:
            groups.pop(SOLVED, None)
        if ENTROPY:
            # The same scale, but a typical group is the geometric mean, which
            # rewards splitting off many small groups more.
            return total * total * 2 ** sum(w / total * math.log2(w / total)
                                             for w in groups.values() if w)
        return sum(w * w for w in groups.values())

    def groups(self, guess: str, answers: list) -> Counter:
        """Total answer weight behind each pattern this guess could show."""
        groups = Counter()
        for answer in answers:
            groups[code(guess, answer)] += self.weights[answer]
        return groups
