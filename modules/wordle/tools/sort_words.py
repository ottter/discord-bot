"""Rebuild words.txt, most likely answer first, and guesses.txt.

    python -m modules.wordle.tools.sort_words

Each line is a word and its weight: roughly the chance it's an answer, from
how common it is today. Plurals, past tenses and the words in unlikely.txt
are rarely answers, so they're cut down to sit near the end. guesses.txt
has the same words weighted by how common they are alone. Needs
`pip install wordfreq`, which the bot itself doesn't.
"""
import math

# Not in requirements.txt, so CI's pylint can't import it.
from wordfreq import zipf_frequency  # pylint: disable=import-error

from modules.wordle.solver import DATA, GUESSES_PATH, WORDS_PATH

UNLIKELY_PATH = DATA / 'unlikely.txt'

# Zipf 3 is a word seen about once per million words. Well above that weighs
# about 1, well below about 0.
MIDPOINT = 3.0
STEEPNESS = 3.0
UNLIKELY_PENALTY = 0.002


def zipf(word):
    """How common a word is, from 0 (never seen) to about 7 ('the')."""
    return zipf_frequency(word, 'en')


def is_inflected(word):
    """A plural or past tense: tears, boxes, lined, asked, tried.

    The stem has to be common, and not much rarer than the word. That keeps
    chaos: 'chao' turns up online, but far less than chaos. -eed words like
    steed are left alone.
    """
    if word.endswith('s') and not word.endswith(('ss', 'us', 'is')):
        stems = [word[:-1], word[:-2]] if word.endswith('es') else [word[:-1]]
    elif word.endswith('ied'):
        stems = [word[:-3] + 'y']
    elif word.endswith('ed') and not word.endswith('eed'):
        stems = [word[:-1], word[:-2]]
    else:
        return False
    floor = max(3, zipf(word) - 1)
    return any(zipf(stem) >= floor for stem in stems)


def read_unlikely():
    """Words from unlikely.txt, skipping # comments."""
    lines = UNLIKELY_PATH.read_text(encoding='utf-8').splitlines()
    return {word for line in lines if not line.startswith('#') for word in line.split()}


def weight(frequency, unlikely, midpoint=MIDPOINT, steepness=STEEPNESS,
           penalty=UNLIKELY_PENALTY):
    """Answer likelihood between 0 and 1, from a word's zipf and whether it's unlikely."""
    likely = 1 / (1 + math.exp(-steepness * (frequency - midpoint)))
    return likely * penalty if unlikely else likely


def read_words():
    """Every word in words.txt, alphabetical."""
    return sorted({line.split()[0] for line in WORDS_PATH.read_text(encoding='utf-8').splitlines()})


def main():
    """Re-weigh every word, ties broken alphabetically so reruns match."""
    words = read_words()
    unlikely = read_unlikely()
    if unlikely - set(words):
        print('Not in the word list:', ' '.join(sorted(unlikely - set(words))))
    frequency = {word: zipf(word) for word in words}
    write(WORDS_PATH, {word: weight(frequency[word], word in unlikely or is_inflected(word))
                       for word in words})
    # What players guess: just how common a word is. Plurals and past tenses
    # are rare answers but ordinary guesses.
    write(GUESSES_PATH, {word: weight(frequency[word], False) for word in words})


def write(path, weights):
    """One word and weight per line, heaviest first."""
    ranked = sorted(weights, key=lambda word: -weights[word])
    with path.open('w', encoding='utf-8', newline='\n') as out:
        out.writelines(f'{word} {weights[word]:.4f}\n' for word in ranked)
    print(f'Wrote {len(ranked)} words to {path}')


if __name__ == '__main__':
    main()
