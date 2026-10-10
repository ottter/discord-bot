"""Try the solver without Discord.

    python -m modules.wordle crane:BBYGB slate:BGYBB   next guess from your board
    python -m modules.wordle --answer stole            watch it play a word

Other players' boards can come from the app's images with --image, or be
typed with --board, e.g. --board BBYBB,BGGBY,GGGGG. Add --easy to drop hard
mode, --vowels for wordle-loser's most-vowels rule, --start to change the opener.
"""
import argparse

from modules.wordle import image
from modules.wordle.boards import Clues
from modules.wordle.games import board
from modules.wordle.solver import Solver, discount, load_used, load_words, play_out, solved
from modules.wordle.storage import distinct

# Past six on purpose: how far over it goes shows how bad a trap was.
TURNS = 20


def play(answer, solver):
    """Guess until solved, printing each row."""
    turns = play_out(answer, solver, TURNS)
    print(board(turns))
    print(f'{len(turns)} guesses' if solved(turns) else f'gave up on {answer}')


def main():
    """Parse the board or the answer and run the matching mode."""
    parser = argparse.ArgumentParser(description='Wordle solver')
    parser.add_argument('rows', nargs='*', help='guess:pattern, e.g. crane:BBYGB')
    parser.add_argument('--answer', help='play against this word')
    parser.add_argument('--start', help='opening guess')
    parser.add_argument('--easy', action='store_true', help='turn hard mode off')
    parser.add_argument('--vowels', action='store_true', help='prefer words with more vowels')
    parser.add_argument('--board', action='append', default=[], metavar='ROWS',
                        help="another player's rows today, e.g. BBYBB,BGGBY,GGGGG")
    parser.add_argument('--image', action='append', default=[], metavar='PATH',
                        help="a results image from the Wordle app")
    args = parser.parse_args()

    boards = [board.upper().split(',') for board in args.board]
    for path in args.image:
        number, found = image.read(path)
        print(f'#{number}:' if number else 'unreadable game number:',
              ' '.join('/'.join(board) for board in found))
        # Only finished boards count, as in Discord.
        boards += distinct(found)

    weights = discount(load_words(), load_used())
    if boards:
        weights = Clues().adjust(weights, boards)
    solver = Solver(weights, vowels=args.vowels, hard=not args.easy)
    if args.start:
        solver.opener = args.start.lower()

    if args.answer:
        play(args.answer.lower(), solver)
        return

    for row in args.rows:
        guess, _, pattern = row.partition(':')
        solver.add(guess, pattern)

    print(f'{len(solver.candidates)} possible: {" ".join(solver.candidates[:10])}')
    print('next guess:', solver.suggest())


if __name__ == '__main__':
    main()
