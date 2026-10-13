"""Average guesses over past Wordle answers, for tuning the solver.

    python -m modules.wordle.tools.bench                  every past answer
    python -m modules.wordle.tools.bench --set SAMPLE=150  try a setting
    python -m modules.wordle.tools.bench --used 0.2       replay a made-up history,
                                                         past answers cut to a fifth
    add --players 5 to that for made-up boards from five other players
"""
import argparse
import random
from collections import Counter
from itertools import islice

from modules.wordle import boards as boards_module
from modules.wordle import solver as solver_module
from modules.wordle.boards import POPULAR, TYPICAL, Clues
from modules.wordle.solver import (GUESSES, GUESSES_PATH, OPENER, Solver, code, discount,
                                   load_listed, load_past, load_words, score, to_pattern)

# Hard mode can wander past six guesses; stop a runaway game well after that.
GIVE_UP = 20
# A made-up history is replayed from here on, so most answers are used, as now.
FIRST_REPLAY = 1400
# Past answers are marked used a block of games at a time, so the cache can
# be shared within a block.
BLOCK = 50


def play(answer, solver, cache) -> int:
    """Guesses taken, or 0 if it gave up.

    The cache maps a board to its suggestion. Games share their early boards,
    so a run only works most of them out once.
    """
    for turn in range(1, GIVE_UP + 1):
        board = tuple(solver.history)
        if board not in cache:
            cache[board] = solver.suggest()
        guess = cache[board]
        if guess is None:
            return 0

        pattern = score(guess, answer)
        if pattern == 'GGGGG':
            return turn
        solver.add(guess, pattern)
    return 0


def made_up_history(answers, weights, args) -> list:
    """The answers in a random order, with repeats of earlier ones mixed in.

    How often NYT repeats is unknown and rising, so the rate is a setting.
    Repeats only start where the replay does. With --off-list, that share of
    replayed answers are swapped for a word off Wordle's original list, the
    way NYT now adds words like yodel.
    """
    rng = random.Random(args.seed)
    fresh = answers[:]
    rng.shuffle(fresh)
    order = fresh[:FIRST_REPLAY]
    swap = random.Random(f'{args.seed} off-list')
    extra = off_list_words(weights, answers) if args.off_list else {}
    for word in fresh[FIRST_REPLAY:]:
        while rng.random() < args.repeat_rate:
            order.append(rng.choice(order))
        if extra and swap.random() < args.off_list:
            word = swap.choices(list(extra), weights=list(extra.values()))[0]
        order.append(word)
    return order


def off_list_words(weights, answers) -> dict:
    """Likely words off the original list that haven't been answers yet. Real
    off-list answers sit around the 600th of these, nearly all in the top 2000."""
    listed, past = load_listed(), set(answers)
    return dict(islice(((word, weight) for word, weight in weights.items()
                        if word not in listed and word not in past), 3000))


def replay(weights, answers, args) -> list:
    """Play the later games of a made-up history, past answers cut down."""
    order = made_up_history(answers, weights, args)
    end = FIRST_REPLAY + args.games if args.games else len(order)
    clues = Clues(weights) if args.players else None
    # Players pick by how common words are, plurals and past tenses included.
    guessed = load_words(GUESSES_PATH)
    typical = dict(islice(guessed.items(), TYPICAL if not args.messy else 3000))
    results = []
    for start in range(FIRST_REPLAY, end, BLOCK):
        cut = discount(weights, Counter(order[:start]), args.used)
        cache = {}
        for number, answer in enumerate(order[start:min(start + BLOCK, end)], start):
            if not clues:
                results.append((answer, play(answer, new_solver(cut, args), cache)))
                continue
            # Each game's made-up boards are different, so nothing can be shared.
            boards = made_up_boards(answer, number, guessed, typical, args)
            results.append((answer, play(answer, new_solver(clues.adjust(cut, boards), args), {})))
    return results


def made_up_boards(answer, number, weights, typical, args) -> list:
    """The other players' boards for one game, the same every run."""
    rng = random.Random(f'{args.seed} {number}')
    return [made_up_board(answer, weights, typical, args, rng) for _ in range(args.players)]


def made_up_board(answer, weights, typical, args, rng) -> list:
    """Another player's rows: an opener, then words that still fit.

    Tidy players pick among the likeliest words that fit; messy ones pick any
    common word that fits. With --odd, that share of guesses is any word at
    all that fits, like opening with something silly. The answer only colors
    their rows, as it would in a real game. Only the rows reach our solver.
    """
    if args.odd and rng.random() < args.odd:
        guess = rng.choice(list(weights))
    elif rng.random() < args.chart_share:
        guess = rng.choices(list(POPULAR), weights=list(POPULAR.values()))[0]
    else:
        guess = rng.choices(list(typical), weights=list(typical.values()))[0]
    left = list(weights)
    rows = []
    for _ in range(GUESSES):
        value = code(guess, answer)
        rows.append(to_pattern(value))
        if rows[-1] == 'GGGGG':
            break
        left = [word for word in left if code(guess, word) == value]
        if args.odd and rng.random() < args.odd:
            guess = rng.choice(left)
        elif args.messy:
            guess = rng.choice([word for word in left if word in typical] or left)
        else:
            likely = left[:20]
            guess = rng.choices(likely, weights=[weights[word] + 1e-9 for word in likely])[0]
    return rows


def new_solver(weights, args) -> Solver:
    """A fresh game with the settings asked for."""
    opener = None if args.start == 'auto' else args.start
    return Solver(weights, opener=opener, vowels=args.vowels, hard=not args.easy)


def main():
    """Play every past answer, or a fixed random handful, with one setting."""
    parser = argparse.ArgumentParser(description='Wordle solver bench')
    parser.add_argument('--games', type=int,
                        help='play this many: picked at random, or the first replayed with --used')
    parser.add_argument('--start', default=OPENER,
                        help="opening guess, or 'auto' to work it out from the boards")
    parser.add_argument('--easy', action='store_true', help='turn hard mode off')
    parser.add_argument('--vowels', action='store_true', help='prefer words with more vowels')
    parser.add_argument('--set', action='append', default=[], metavar='NAME=VALUE',
                        help='change a setting in solver.py or boards.py, e.g. SAMPLE=600')
    parser.add_argument('--used', type=float, metavar='FACTOR',
                        help='replay a made-up history with past answers cut to this')
    parser.add_argument('--seed', type=int, default=0, help='which made-up history')
    parser.add_argument('--players', type=int, default=0,
                        help='with --used, made-up boards from this many other players')
    parser.add_argument('--chart-share', type=float, default=sum(POPULAR.values()),
                        help='how often those players open with a popular opener')
    parser.add_argument('--messy', action='store_true',
                        help='those players pick any common word that fits, not likely ones')
    parser.add_argument('--odd', type=float, default=0,
                        help='share of those guesses that are any word that fits')
    # Reuse began on 2 Feb 2026 (#1689); 25 of the ~248 games since were repeats.
    parser.add_argument('--repeat-rate', type=float, default=0.1,
                        help='share of replayed games that repeat an earlier answer')
    parser.add_argument('--off-list', type=float, default=0,
                        help='with --used, share of replayed answers off the original list')
    parser.add_argument('--half', choices=('tune', 'check'),
                        help='tune settings on one half, confirm on the other')
    args = parser.parse_args()
    for setting in args.set:
        change(*setting.split('=', 1))

    weights = load_words()
    answers = [word for _, word in load_past()]
    if args.used is not None:
        report(replay(weights, answers, args))
        return
    if args.half:
        # The same split as tune_weights.py.
        random.Random(0).shuffle(answers)
        answers = answers[::2] if args.half == 'tune' else answers[1::2]
    if args.games:
        answers = random.Random(0).sample(answers, args.games)

    cache = {}
    report([(answer, play(answer, new_solver(weights, args), cache)) for answer in answers])


def change(name, value):
    """Set one setting by name, from text like 'False' or '0.5'."""
    module = solver_module if hasattr(solver_module, name) else boards_module
    current = getattr(module, name)
    if isinstance(current, bool):
        setattr(module, name, value.lower() in ('true', '1', 'yes'))
    else:
        setattr(module, name, type(current)(value))


def report(results):
    """Average guesses and the games lost, from (answer, guesses) pairs."""
    solved = [turns for _, turns in results if turns]
    lost = sorted(answer for answer, turns in results if not turns or turns > 6)
    print(f'{sum(solved) / len(solved):.3f} average over {len(results)}, worst {max(solved)}')
    print(f'lost {len(lost)}:', ' '.join(lost))


if __name__ == '__main__':
    main()
