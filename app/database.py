from pathlib import Path
import sqlite3

DATABASE = Path(__file__).parent.parent / "database" / "dpm.db"


def get_connection() -> sqlite3.Connection:
    """
    Return a SQLite connection configured for DPM.
    """

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")

    return conn