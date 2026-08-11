"""
Database infrastructure for DPM.

Owns SQLite connection creation and transaction management.
Contains no Flask route or business logic.
"""

from contextlib import contextmanager
import sqlite3

from app.config import DATABASE_PATH, SCHEMA_PATH


def get_connection() -> sqlite3.Connection:
    """Return a configured SQLite connection."""

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


@contextmanager
def database_connection():
    """
    Provide a managed database connection.

    Commits automatically on success and rolls back automatically
    when an exception occurs.
    """

    conn = get_connection()

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def initialize_database() -> None:
    """Create the database schema."""

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Database schema not found: {SCHEMA_PATH}"
        )

    with database_connection() as conn:
        schema = SCHEMA_PATH.read_text(
            encoding="utf-8",
        )

        conn.executescript(schema)