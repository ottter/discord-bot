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

CREATE TABLE IF NOT EXISTS boards (
    guild_id INTEGER NOT NULL,
    game     INTEGER NOT NULL,
    rows     TEXT    NOT NULL,
    seen_at  TEXT    NOT NULL,
    PRIMARY KEY (guild_id, game)
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

    def save_boards(self, guild_id, game, boards) -> None:
        """The newest image's boards for a game. The app edits one message per
        game as people play, so the newest image always has every board."""
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO boards (guild_id, game, rows, seen_at) VALUES (?, ?, ?, ?)
                   ON CONFLICT (guild_id, game) DO UPDATE SET
                       rows=excluded.rows, seen_at=excluded.seen_at""",
                (guild_id, game, json.dumps(boards), now()))

    def boards(self, guild_id, game) -> list:
        """Every board seen for a game, each a list of rows like 'BYBGB'."""
        with self.connect() as conn:
            row = conn.execute('SELECT rows FROM boards WHERE guild_id=? AND game=?',
                               (guild_id, game)).fetchone()
        return json.loads(row['rows']) if row else []

    def latest_game(self, guild_id):
        """The newest game number seen in this guild, or None."""
        with self.connect() as conn:
            row = conn.execute('SELECT MAX(game) AS game FROM boards WHERE guild_id=?',
                               (guild_id,)).fetchone()
        return row['game']

    # -- solves ------------------------------------------------------------

    def save_solve(self, guild_id, game, turns, boards) -> bool:
        """Lock in the bot's result for a game, replacing a provisional one.
        Returns False if one was already locked, which then stays."""
        return self.save((guild_id, game), turns, boards, locked=True)

    def save_play(self, guild_id, game, turns, boards) -> None:
        """A provisional result from /wordle play. The last one stands if the
        game never gets enough boards to lock in."""
        self.save((guild_id, game), turns, boards, locked=False)

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


def now() -> str:
    """A timestamp for the database."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
