"""SQLite storage for Wordle answers, boards seen, and the bot's solves.

One file, stdlib only. The path comes from WORDLE_DB; in a container, mount a
volume there so answers and solves survive a restart.
"""
import datetime
import json
import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path

log = logging.getLogger('discord.bot')

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / 'data' / 'wordle.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS answers (
    game       INTEGER PRIMARY KEY,
    word       TEXT    NOT NULL,
    fetched_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS images (
    guild_id   INTEGER NOT NULL,
    game       INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    rows       TEXT    NOT NULL,
    seen_at    TEXT    NOT NULL,
    PRIMARY KEY (guild_id, game, message_id)
);

CREATE TABLE IF NOT EXISTS solves (
    guild_id  INTEGER NOT NULL,
    game      INTEGER NOT NULL,
    turns     TEXT    NOT NULL,
    boards    INTEGER NOT NULL,
    solved_at TEXT    NOT NULL,
    locked    INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (guild_id, game)
);

CREATE TABLE IF NOT EXISTS guild_config (
    guild_id   INTEGER PRIMARY KEY,
    channel_id INTEGER
);
"""


class WordleDB:
    """Every query the cogs need. Connections are per-operation and short."""

    def __init__(self, path=None):
        self.path = Path(path or DEFAULT_DB_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript(SCHEMA)
            # Files made before results could be provisional.
            columns = [row['name'] for row in conn.execute('PRAGMA table_info(solves)')]
            if 'locked' not in columns:
                conn.execute('ALTER TABLE solves ADD COLUMN locked INTEGER NOT NULL DEFAULT 1')
            # Files made when only the newest image per game was kept.
            if conn.execute("SELECT 1 FROM sqlite_master WHERE name='boards'").fetchone():
                conn.execute("""INSERT OR IGNORE INTO images
                                SELECT guild_id, game, 0, rows, seen_at FROM boards""")
                conn.execute('DROP TABLE boards')
        log.info('Wordle database ready at %s', self.path)

    @contextmanager
    def connect(self):
        """A short-lived connection. sqlite3 commits it on success and rolls it
        back if the block raises."""
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    # -- answers -----------------------------------------------------------

    def answer(self, game):
        """A game's answer, or None if it hasn't been looked up."""
        with self.connect() as conn:
            row = conn.execute('SELECT word FROM answers WHERE game=?', (game,)).fetchone()
        return row['word'] if row else None

    def save_answer(self, game, word) -> None:
        """Remember a game's answer. It never changes, so the first one stays."""
        with self.connect() as conn:
            conn.execute('INSERT OR IGNORE INTO answers (game, word, fetched_at) VALUES (?, ?, ?)',
                         (game, word, now()))

    def answers_before(self, game) -> list:
        """(game, word) for every stored game before this one."""
        with self.connect() as conn:
            rows = conn.execute('SELECT game, word FROM answers WHERE game < ?', (game,)).fetchall()
        return [(row['game'], row['word']) for row in rows]

    # -- boards ------------------------------------------------------------

    def save_image(self, guild_id, game, message_id, boards) -> None:
        """The boards in one of the app's posts. It edits a post as people
        play, so a newer image of the same post replaces the older one."""
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO images (guild_id, game, message_id, rows, seen_at)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT (guild_id, game, message_id) DO UPDATE SET
                       rows=excluded.rows, seen_at=excluded.seen_at""",
                (guild_id, game, message_id, json.dumps(boards), now()))

    def boards(self, guild_id, game) -> list:
        """This guild's boards for a game, from all its posts, each once."""
        with self.connect() as conn:
            rows = conn.execute('SELECT rows FROM images WHERE guild_id=? AND game=?',
                                (guild_id, game)).fetchall()
        return distinct(board for row in rows for board in json.loads(row['rows']))

    def pooled(self, game) -> list:
        """Every guild's boards for a game, each once. Plays use these."""
        with self.connect() as conn:
            rows = conn.execute('SELECT rows FROM images WHERE game=?', (game,)).fetchall()
        return distinct(board for row in rows for board in json.loads(row['rows']))

    def latest_game(self, guild_id=None):
        """The newest game number seen in this guild, or in any guild."""
        with self.connect() as conn:
            if guild_id is None:
                row = conn.execute('SELECT MAX(game) AS game FROM images').fetchone()
            else:
                row = conn.execute('SELECT MAX(game) AS game FROM images WHERE guild_id=?',
                                   (guild_id,)).fetchone()
        return row['game']

    def first_answer(self):
        """The oldest game whose answer is stored, or None. Only days the bot
        played are stored, so games before it are from before it started."""
        with self.connect() as conn:
            return conn.execute('SELECT MIN(game) AS game FROM answers').fetchone()['game']

    def open_games(self, before) -> list:
        """(guild_id, game) for games before this one that had boards or a
        /wordle play in a guild but never locked in there."""
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT guild_id, game FROM images WHERE game < :before
                   UNION SELECT guild_id, game FROM solves WHERE game < :before
                   EXCEPT SELECT guild_id, game FROM solves WHERE locked = 1""",
                {'before': before}).fetchall()
        return [(row['guild_id'], row['game']) for row in rows]

    # -- solves ------------------------------------------------------------

    def save_solve(self, guild_id, game, turns, boards) -> bool:
        """Lock in the bot's result for a game, replacing a provisional one.
        Returns False if one was already locked, which then stays."""
        return self.save((guild_id, game), turns, boards, locked=True)

    def save_play(self, guild_id, game, turns, boards) -> None:
        """A provisional result from /wordle play. The last one stands if the
        game never gets enough boards to lock in."""
        self.save((guild_id, game), turns, boards, locked=False)

    def lock(self, guild_id, game) -> None:
        """Lock in whatever result is saved, as it is."""
        with self.connect() as conn:
            conn.execute('UPDATE solves SET locked = 1 WHERE guild_id=? AND game=?',
                         (guild_id, game))

    def save(self, key, turns, boards, locked) -> bool:
        """Save a result unless one's locked in. True if it was saved."""
        guild_id, game = key
        with self.connect() as conn:
            cur = conn.execute(
                """INSERT INTO solves (guild_id, game, turns, boards, solved_at, locked)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT (guild_id, game) DO UPDATE SET
                       turns=excluded.turns, boards=excluded.boards,
                       solved_at=excluded.solved_at, locked=excluded.locked
                   WHERE solves.locked = 0""",
                (guild_id, game, json.dumps(turns), boards, now(), int(locked)))
            return cur.rowcount == 1

    def solve(self, guild_id, game):
        """(turns, boards used, locked) for a saved result, or None."""
        with self.connect() as conn:
            row = conn.execute(
                'SELECT turns, boards, locked FROM solves WHERE guild_id=? AND game=?',
                (guild_id, game)).fetchone()
        if row is None:
            return None
        return json.loads(row['turns']), row['boards'], bool(row['locked'])

    # -- per-guild settings ------------------------------------------------

    def set_channel(self, guild_id, channel_id) -> None:
        """Where locked results post. None means the Wordle app's own channel."""
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO guild_config (guild_id, channel_id) VALUES (?, ?)
                   ON CONFLICT (guild_id) DO UPDATE SET channel_id=excluded.channel_id""",
                (guild_id, channel_id))

    def channel(self, guild_id):
        """The configured channel id, or None."""
        with self.connect() as conn:
            row = conn.execute('SELECT channel_id FROM guild_config WHERE guild_id=?',
                               (guild_id,)).fetchone()
        return row['channel_id'] if row else None


def distinct(boards) -> list:
    """Finished boards, each once. A board still being played doesn't count
    until a later image shows it solved or out of guesses, and the same board
    in two posts counts once."""
    finished = {tuple(board) for board in boards if done(board)}
    return [list(board) for board in sorted(finished)]


def done(board) -> bool:
    """Solved, or all six rows used without solving (X/6)."""
    return bool(board) and (board[-1] == 'GGGGG' or len(board) >= 6)


def now() -> str:
    """A timestamp for the database."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
