"""
Database infrastructure for DPM.

This module owns SQLite connection creation and database initialization.
It contains no Flask route or business logic.
"""

from pathlib import Path
import sqlite3

from app.config import DATABASE_PATH, SCHEMA_PATH


def get_connection() -> sqlite3.Connection:
    """
    Return a configured SQLite connection.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(
        DATABASE_PATH,
    )

    conn.row_factory = sqlite3.Row

    # Enforce relational integrity.
    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


def initialize_database() -> None:
    """
    Create/update the database schema.

    Schema creation is intentionally idempotent and safe to execute
    during application startup.
    """

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Database schema not found: {SCHEMA_PATH}"
        )

    conn = get_connection()

    try:
        schema = SCHEMA_PATH.read_text(
            encoding="utf-8",
        )

        conn.executescript(schema)
        conn.commit()

    finally:
        conn.close()