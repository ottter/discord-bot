"""Find the weight settings that best predict real Wordle answers.

    python -m modules.wordle.tools.tune_weights

Scores each setting by how likely its weights make the past answers, without
playing any games. Tunes on half the answers and reports the other half too,
so settings that only memorize the first half show up. Copy the winner into
sort_words.py.
"""
import itertools
import math
import random

from modules.wordle.solver import load_past
from modules.wordle.tools.sort_words import (MIDPOINT, STEEPNESS, UNLIKELY_PENALTY, is_inflected,
                                       read_unlikely, read_words, weight, zipf)

MIDPOINTS = [1.5 + 0.25 * i for i in range(11)]       # 1.5 to 4.0
STEEPNESSES = [0.5 * i for i in range(1, 11)]          # 0.5 to 5.0
PENALTIES = [1, 0.3, 0.1, 0.03, 0.01, 0.002]


def fit(words, answers, setting):
    """Average log chance of each answer, if answers were drawn by weight.

    Higher is better. Every word's weight counts against it, so a setting
    can't win by weighing everything high.
    """
    weights = {word: weight(*words[word], *setting) for word in words}
    total = math.log(sum(weights.values()))
    return sum(math.log(weights[answer]) for answer in answers) / len(answers) - total


def main():
    """Grid search, best few printed with both halves' scores."""
    unlikely = read_unlikely()
    words = {word: (zipf(word), word in unlikely or is_inflected(word)) for word in read_words()}
    past = [word for _, word in load_past()]
    random.Random(0).shuffle(past)
    tune, check = past[::2], past[1::2]
    print(f'{sum(words[a][1] for a in past)} of {len(past)} past answers are marked unlikely')

    results = sorted(((fit(words, tune, setting), setting) for setting in
                      itertools.product(MIDPOINTS, STEEPNESSES, PENALTIES)), reverse=True)

    def row(setting):
        midpoint, steepness, penalty = setting
        return (f'{midpoint:8.2f} {steepness:10.1f} {penalty:7g}  '
                f'{fit(words, tune, setting):6.3f} {fit(words, check, setting):6.3f}')

    print('midpoint steepness penalty   tune  check')
    for _, setting in results[:8]:
        print(row(setting))
    print('current:', row((MIDPOINT, STEEPNESS, UNLIKELY_PENALTY)))


if __name__ == '__main__':
    main()
