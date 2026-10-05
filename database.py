import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from config import DB_PATH
from logger import log


def _connect():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


@contextmanager
def db():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with db() as conn:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS mutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                until TEXT,
                reason TEXT,
                shadow INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                UNIQUE(user_id, target_id)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS mute_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                word TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(user_id, word)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                msg_count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, chat_id, date)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS msg_cache (
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                msg_id INTEGER NOT NULL,
                sender_id INTEGER,
                sender_name TEXT,
                text TEXT,
                media_type TEXT,
                date TEXT NOT NULL,
                PRIMARY KEY (user_id, chat_id, msg_id)
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_cache_date ON msg_cache(date)")

    log.info("База данных инициализирована")


def cleanup_old_data(days=30):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM msg_cache WHERE date < ?", (cutoff,))
        c.execute("DELETE FROM stats WHERE date < ?", (cutoff[:10],))
    log.info(f"Очищены данные старше {days} дней")