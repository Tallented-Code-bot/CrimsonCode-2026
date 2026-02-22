import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "database.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


@contextmanager
def get_db():
    """Yield a connected, row-factory-enabled SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create all tables if they don't already exist."""
    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()
    with get_db() as db:
        db.executescript(schema)


# ── Admin helpers ──────────────────────────────────────────────────────────────

def get_admin(username: str):
    """Return the admin row for username, or None."""
    with get_db() as db:
        return db.execute(
            "SELECT * FROM admins WHERE username = ?", (username,)
        ).fetchone()


# ── Event helpers ──────────────────────────────────────────────────────────────

def get_recent_events(limit: int = 20):
    """Return the most recent detection events, newest first."""
    with get_db() as db:
        return db.execute(
            "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()


def insert_event(person_name: str, confidence: float = None, image_path: str = None):
    """Insert a new detection event. Called by the camera/ML pipeline."""
    with get_db() as db:
        db.execute(
            "INSERT INTO events (person_name, confidence, image_path) VALUES (?, ?, ?)",
            (person_name, confidence, image_path),
        )
