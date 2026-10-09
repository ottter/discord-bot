"""Read the Wordle app's result images: the game number and each board's rows.

The tiles are flat colors, so finding them is just finding those colors.
The number in the title is matched against digits.json, one small grayscale
shape per digit taken from real images: 12 rows of 8, 0 dark to 255 bright.
"""
import json

from PIL import Image

from modules.wordle.solver import DATA

DIGITS_PATH = DATA / 'digits.json'
TILES = {(83, 141, 78): 'G', (181, 159, 59): 'Y', (58, 58, 60): 'B', (18, 18, 19): '.'}
# How far a pixel can be from a tile color and still count. Kept tight: the
# background is only 3 off the empty tile color.
CLOSE = 2
# A tile column or row has at least this many tile pixels in it.
TILE_PIXELS = 15
# Text is any pixel brighter than this on the dark background.
INK = 60
# Gaps wider than this split words in the title, and boards from each other.
WORD_GAP = 3
BOARD_GAP = 8
# A digit counts only if it's this close to one shape and clearly closer to it
# than to any other.
MATCH = 20
MARGIN = 10
SHAPE = (8, 12)


def read(path) -> tuple:
    """(game number or None if unreadable, boards as lists of rows like 'BYBGB')."""
    image = Image.open(path).convert('RGB')
    return game_number(image), boards(image)


def tile(pixel):
    """The tile letter for a pixel, or None if it isn't a tile color."""
    for color, letter in TILES.items():
        if all(abs(a - b) <= CLOSE for a, b in zip(pixel, color)):
            return letter
    return None


def boards(image) -> list:
    """Each board's played rows, left to right then top to bottom.

    Big groups come as more than one row of boards, so each row of boards is
    found first, then the boards across it. Empty rows are left off.
    """
    width, height = image.size
    pixels = image.load()
    is_tile = [[tile(pixels[x, y]) is not None for x in range(width)] for y in range(height)]
    rows = spans([sum(row) >= TILE_PIXELS for row in is_tile])

    found = []
    for band in split(rows, BOARD_GAP):
        lines = is_tile[band[0][0]:band[-1][1]]
        columns = spans([sum(line[x] for line in lines) >= TILE_PIXELS for x in range(width)])
        for group in split(columns, BOARD_GAP):
            found.append(read_board(pixels, band, group))
    return found


def read_board(pixels, rows, columns) -> list:
    """One board's rows, stopping at the first one not played yet."""
    board = []
    for top, bottom in rows:
        row = ''.join(tile(pixels[(left + right) // 2, (top + bottom) // 2]) or '?'
                      for left, right in columns)
        if '.' in row:
            break
        board.append(row)
    return board


def game_number(image):
    """The number after 'Wordle No.', or None if any digit isn't a clear match."""
    gray = image.convert('L')
    width, height = gray.size
    pixels = gray.load()
    lit = [any(pixels[x, y] > INK for x in range(width)) for y in range(height)]
    if True not in lit:
        return None
    top = lit.index(True)
    bottom = top
    while bottom + 1 < height and lit[bottom + 1]:
        bottom += 1

    title = gray.crop((0, top - 1, width, bottom + 2))
    pixels = title.load()
    glyphs = spans([any(pixels[x, y] > INK for y in range(title.size[1]))
                    for x in range(width)], least=1)
    number = split(glyphs, WORD_GAP)[-1]

    digits = ''
    for left, right in number:
        digit = closest(shape(title.crop((left, 0, right, title.size[1]))))
        if digit is None:
            return None
        digits += digit
    return int(digits)


def shape(glyph) -> list:
    """A glyph trimmed to its ink and scaled to a fixed size, as a flat list."""
    glyph = glyph.crop(glyph.point(lambda value: 255 if value > INK else 0).getbbox())
    return list(glyph.resize(SHAPE, Image.Resampling.BILINEAR).getdata())


def closest(found):
    """The digit whose shape is nearest, if it's a clear match."""
    distances = sorted((sum(abs(a - b) for a, b in zip(found, known)) / len(known), digit)
                       for digit, known in load_digits().items())
    (best, digit), (second, _) = distances[0], distances[1]
    return digit if best <= MATCH and second - best >= MARGIN else None


def load_digits() -> dict:
    """Digit to shape, from digits.json, where each is a grid of rows."""
    grids = json.loads(DIGITS_PATH.read_text(encoding='utf-8'))
    return {digit: [value for row in grid for value in row] for digit, grid in grids.items()}


def spans(flags, least=8) -> list:
    """(start, end) of each run of True at least this long."""
    found, start = [], None
    for i, flag in enumerate(flags + [False]):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            if i - start >= least:
                found.append((start, i))
            start = None
    return found


def split(runs, gap) -> list:
    """Group runs that sit closer together than gap."""
    groups = []
    for run in runs:
        if groups and run[0] - groups[-1][-1][1] <= gap:
            groups[-1].append(run)
        else:
            groups.append([run])
    return groups
