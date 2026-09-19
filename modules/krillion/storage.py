"""SQLite storage for Krillion scores and per-guild settings.

One file, stdlib only. The path comes from KRILLION_DB; in a container that
wants scores to survive a restart, mount a volume there.
"""
import logging
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

log = logging.getLogger('discord.bot')

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = REPO_ROOT / 'data' / 'krillion.db'


def db_path(configured=None) -> Path:
    """Config wins, then the environment, then data/krillion.db."""
    return Path(configured or os.environ.get('DISCORD_BOT_KRILLION_DB')
                or DEFAULT_DB_PATH)

SCHEMA = """
CREATE TABLE IF NOT EXISTS scores (
    guild_id     INTEGER NOT NULL,
    user_id      INTEGER NOT NULL,
    day          INTEGER NOT NULL,
    score        INTEGER NOT NULL,
    emoji        TEXT    NOT NULL,
    submitted_at TEXT    NOT NULL,
    PRIMARY KEY (guild_id, user_id, day)
);

CREATE INDEX IF NOT EXISTS scores_by_day ON scores (guild_id, day, score DESC);

CREATE TABLE IF NOT EXISTS guild_config (
    guild_id           INTEGER PRIMARY KEY,
    results_channel_id INTEGER,
    last_posted_day    INTEGER
);
"""


class KrillionDB:
    """Every query the cogs need. Connections are per-operation and short."""

    def __init__(self, path=None):
        self.path = db_path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript(SCHEMA)
        log.info('Krillion database ready at %s', self.path)

    @contextmanager
    def connect(self):
        """Commits on success, rolls back if the block raises."""
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # -- scores ------------------------------------------------------------

    def save_score(self, guild_id, user_id, result, submitted_at) -> int:
        """Store a parsed share, replacing any earlier one for the same day.

        Returns the score it replaced, or None if this is the first submission.
        """
        day = result['day']
        with self.connect() as conn:
            row = conn.execute(
                'SELECT score FROM scores WHERE guild_id=? AND user_id=? AND day=?',
                (guild_id, user_id, day)).fetchone()
            conn.execute(
                """INSERT INTO scores (guild_id, user_id, day, score, emoji, submitted_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT (guild_id, user_id, day) DO UPDATE SET
                       score=excluded.score,
                       emoji=excluded.emoji,
                       submitted_at=excluded.submitted_at""",
                (guild_id, user_id, day, result['score'], result['emoji'], submitted_at))
        return row['score'] if row else None

    def leaderboard(self, guild_id, day) -> list:
        """One day's scores, best first, earliest submission breaking ties."""
        with self.connect() as conn:
            return conn.execute(
                """SELECT user_id, score, emoji, submitted_at FROM scores
                   WHERE guild_id=? AND day=?
                   ORDER BY score DESC, submitted_at ASC""",
                (guild_id, day)).fetchall()

    def user_stats(self, guild_id, user_id) -> sqlite3.Row:
        """Games played, average, best and total for one member."""
        with self.connect() as conn:
            return conn.execute(
                """SELECT COUNT(*) AS played, AVG(score) AS average,
                          MAX(score) AS best, SUM(score) AS total
                   FROM scores WHERE guild_id=? AND user_id=?""",
                (guild_id, user_id)).fetchone()

    def user_days(self, guild_id, user_id) -> list:
        """Every day this member has played, newest first — used for streaks."""
        with self.connect() as conn:
            rows = conn.execute(
                'SELECT day FROM scores WHERE guild_id=? AND user_id=? ORDER BY day DESC',
                (guild_id, user_id)).fetchall()
        return [row['day'] for row in rows]

    def clear(self, guild_id, day=None) -> int:
        """Delete this guild's scores, or just one day's. Returns rows removed."""
        with self.connect() as conn:
            if day is None:
                cur = conn.execute('DELETE FROM scores WHERE guild_id=?', (guild_id,))
            else:
                cur = conn.execute(
                    'DELETE FROM scores WHERE guild_id=? AND day=?', (guild_id, day))
            return cur.rowcount

    # -- per-guild settings ------------------------------------------------

    def set_results_channel(self, guild_id, channel_id) -> None:
        """Set where the daily results post. None turns posting off."""
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO guild_config (guild_id, results_channel_id) VALUES (?, ?)
                   ON CONFLICT (guild_id) DO UPDATE
                       SET results_channel_id=excluded.results_channel_id""",
                (guild_id, channel_id))

    def results_channel(self, guild_id):
        """The configured channel id, or None if the guild hasn't set one."""
        with self.connect() as conn:
            row = conn.execute(
                'SELECT results_channel_id FROM guild_config WHERE guild_id=?',
                (guild_id,)).fetchone()
        return row['results_channel_id'] if row else None

    def guilds_awaiting(self, day) -> list:
        """Guilds with a results channel that haven't been posted this day yet."""
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT guild_id, results_channel_id FROM guild_config
                   WHERE results_channel_id IS NOT NULL
                     AND (last_posted_day IS NULL OR last_posted_day < ?)""",
                (day,)).fetchall()
        return [(row['guild_id'], row['results_channel_id']) for row in rows]

    def mark_posted(self, guild_id, day) -> None:
        """Remember we posted this day, so a restart doesn't post it twice."""
        with self.connect() as conn:
            conn.execute(
                'UPDATE guild_config SET last_posted_day=? WHERE guild_id=?', (day, guild_id))
