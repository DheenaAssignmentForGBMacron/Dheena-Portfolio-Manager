"""
Database infrastructure for DPM.

Owns SQLite connection creation, transaction management,
schema initialization, and database migrations.

Contains no Flask route or business logic.
"""

from contextlib import contextmanager
import sqlite3

from app.config import DATABASE_PATH, SCHEMA_PATH


CURRENT_SCHEMA_VERSION = 2


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

    Commits automatically on success and rolls back
    automatically when an exception occurs.
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


def _table_exists(conn, table_name: str) -> bool:
    """Return True when a table exists."""

    row = conn.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (table_name,),
    ).fetchone()

    return row is not None


def _column_exists(
    conn,
    table_name: str,
    column_name: str,
) -> bool:
    """Return True when a table contains a column."""

    if not _table_exists(conn, table_name):
        return False

    columns = conn.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return any(
        column["name"] == column_name
        for column in columns
    )


def _ensure_schema_version_table(conn) -> None:
    """Create the schema version table if required."""

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL
        )
        """
    )

    row = conn.execute(
        """
        SELECT version
        FROM schema_version
        LIMIT 1
        """
    ).fetchone()

    if row is None:
        conn.execute(
            """
            INSERT INTO schema_version(version)
            VALUES (0)
            """
        )


def _get_schema_version(conn) -> int:
    """Return the current database schema version."""

    row = conn.execute(
        """
        SELECT version
        FROM schema_version
        LIMIT 1
        """
    ).fetchone()

    return int(row["version"])


def _set_schema_version(
    conn,
    version: int,
) -> None:
    """Persist the database schema version."""

    conn.execute(
        """
        UPDATE schema_version
        SET version = ?
        """,
        (version,),
    )


def _migrate_snapshot_schema(conn) -> None:
    """
    Migrate the original snapshot schema to the current model.

    Legacy portfolio snapshots contained:

        current_value
        profit

    The current model separates:

        current
        realized_pl
        unrealized_pl
        total_pl

    Existing historical profit is preserved as unrealized/total
    profit because the legacy schema did not retain the realized
    vs unrealized split.
    """

    # -------------------------------------------------
    # Portfolio snapshots
    # -------------------------------------------------

    if _table_exists(conn, "portfolio_snapshots"):

        if not _column_exists(
            conn,
            "portfolio_snapshots",
            "current",
        ):
            conn.execute(
                """
                ALTER TABLE portfolio_snapshots
                ADD COLUMN current REAL
                """
            )

            conn.execute(
                """
                UPDATE portfolio_snapshots
                SET current = current_value
                WHERE current IS NULL
                """
            )

        if not _column_exists(
            conn,
            "portfolio_snapshots",
            "realized_pl",
        ):
            conn.execute(
                """
                ALTER TABLE portfolio_snapshots
                ADD COLUMN realized_pl REAL DEFAULT 0
                """
            )

        if not _column_exists(
            conn,
            "portfolio_snapshots",
            "unrealized_pl",
        ):
            conn.execute(
                """
                ALTER TABLE portfolio_snapshots
                ADD COLUMN unrealized_pl REAL
                """
            )

            conn.execute(
                """
                UPDATE portfolio_snapshots
                SET unrealized_pl = profit
                WHERE unrealized_pl IS NULL
                """
            )

        if not _column_exists(
            conn,
            "portfolio_snapshots",
            "total_pl",
        ):
            conn.execute(
                """
                ALTER TABLE portfolio_snapshots
                ADD COLUMN total_pl REAL
                """
            )

            conn.execute(
                """
                UPDATE portfolio_snapshots
                SET total_pl = profit
                WHERE total_pl IS NULL
                """
            )

    # -------------------------------------------------
    # Asset snapshots
    # -------------------------------------------------

    if _table_exists(conn, "asset_snapshots"):

        if not _column_exists(
            conn,
            "asset_snapshots",
            "realized_pl",
        ):
            conn.execute(
                """
                ALTER TABLE asset_snapshots
                ADD COLUMN realized_pl REAL DEFAULT 0
                """
            )

        if not _column_exists(
            conn,
            "asset_snapshots",
            "unrealized_pl",
        ):
            conn.execute(
                """
                ALTER TABLE asset_snapshots
                ADD COLUMN unrealized_pl REAL
                """
            )

            conn.execute(
                """
                UPDATE asset_snapshots
                SET unrealized_pl = profit
                WHERE unrealized_pl IS NULL
                """
            )

        if not _column_exists(
            conn,
            "asset_snapshots",
            "total_pl",
        ):
            conn.execute(
                """
                ALTER TABLE asset_snapshots
                ADD COLUMN total_pl REAL
                """
            )

            conn.execute(
                """
                UPDATE asset_snapshots
                SET total_pl = profit
                WHERE total_pl IS NULL
                """
            )


def _run_migrations(conn) -> None:
    """Run all pending database migrations."""

    _ensure_schema_version_table(conn)

    version = _get_schema_version(conn)

    if version < 1:
        _migrate_snapshot_schema(conn)
        _set_schema_version(conn, 1)
        version = 1

    if version < 2:
        _set_schema_version(conn, 2)


def initialize_database() -> None:
    """
    Create the database schema and run pending migrations.

    Existing user data is preserved.
    """

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Database schema not found: {SCHEMA_PATH}"
        )

    with database_connection() as conn:

        schema = SCHEMA_PATH.read_text(
            encoding="utf-8",
        )

        conn.executescript(schema)

        _run_migrations(conn)