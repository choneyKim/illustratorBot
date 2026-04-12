import sqlite3
import logging
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "bot.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id            INTEGER PRIMARY KEY,
                username           TEXT,
                first_name         TEXT,
                registered_at      TEXT DEFAULT (date('now')),
                current_week       INTEGER DEFAULT 1,
                current_day        INTEGER DEFAULT 0,
                assignment_status  TEXT DEFAULT 'none',
                retry_count        INTEGER DEFAULT 0,
                total_days_studied INTEGER DEFAULT 0,
                notifications_on   INTEGER DEFAULT 1,
                last_notified_date TEXT DEFAULT NULL
            );

            CREATE TABLE IF NOT EXISTS lesson_cache (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id     INTEGER NOT NULL,
                week        INTEGER NOT NULL,
                day         INTEGER NOT NULL,
                content     TEXT NOT NULL,
                assignment  TEXT,
                created_at  TEXT DEFAULT (datetime('now')),
                UNIQUE(chat_id, week, day),
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
            );

            CREATE TABLE IF NOT EXISTS submissions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id      INTEGER NOT NULL,
                week         INTEGER NOT NULL,
                submitted_at TEXT DEFAULT (datetime('now')),
                feedback     TEXT,
                passed       INTEGER DEFAULT 0,
                retry_count  INTEGER DEFAULT 0,
                FOREIGN KEY (chat_id) REFERENCES users(chat_id)
            );
        """)
    logger.info("Database initialized")


# ─── User operations ────────────────────────────────────────────────────────

def get_user(chat_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE chat_id = ?", (chat_id,)
        ).fetchone()


def create_user(chat_id: int, username: str, first_name: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO users (chat_id, username, first_name,
               current_week, current_day, assignment_status)
               VALUES (?, ?, ?, 1, 1, 'none')""",
            (chat_id, username, first_name),
        )


def get_all_active_users() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE notifications_on = 1"
        ).fetchall()


def update_user_progress(chat_id: int, week: int, day: int,
                         assignment_status: str, retry_count: int = 0) -> None:
    with get_connection() as conn:
        conn.execute(
            """UPDATE users SET current_week=?, current_day=?,
               assignment_status=?, retry_count=?,
               total_days_studied = total_days_studied + 1,
               last_notified_date = ?
               WHERE chat_id = ?""",
            (week, day, assignment_status, retry_count,
             date.today().isoformat(), chat_id),
        )


def set_last_notified(chat_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET last_notified_date = ? WHERE chat_id = ?",
            (date.today().isoformat(), chat_id),
        )


def set_assignment_status(chat_id: int, status: str, retry_count: int | None = None) -> None:
    if retry_count is not None:
        with get_connection() as conn:
            conn.execute(
                "UPDATE users SET assignment_status=?, retry_count=? WHERE chat_id=?",
                (status, retry_count, chat_id),
            )
    else:
        with get_connection() as conn:
            conn.execute(
                "UPDATE users SET assignment_status=? WHERE chat_id=?",
                (status, chat_id),
            )


# ─── Lesson cache ────────────────────────────────────────────────────────────

def get_cached_lesson(chat_id: int, week: int, day: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM lesson_cache WHERE chat_id=? AND week=? AND day=?",
            (chat_id, week, day),
        ).fetchone()


def save_lesson_cache(chat_id: int, week: int, day: int,
                      content: str, assignment: str = "") -> None:
    with get_connection() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO lesson_cache
               (chat_id, week, day, content, assignment)
               VALUES (?, ?, ?, ?, ?)""",
            (chat_id, week, day, content, assignment),
        )


# ─── Submissions ─────────────────────────────────────────────────────────────

def save_submission(chat_id: int, week: int, feedback: str,
                    passed: bool, retry_count: int) -> None:
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO submissions (chat_id, week, feedback, passed, retry_count)
               VALUES (?, ?, ?, ?, ?)""",
            (chat_id, week, feedback, int(passed), retry_count),
        )


def get_latest_submission(chat_id: int, week: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            """SELECT * FROM submissions WHERE chat_id=? AND week=?
               ORDER BY submitted_at DESC LIMIT 1""",
            (chat_id, week),
        ).fetchone()
