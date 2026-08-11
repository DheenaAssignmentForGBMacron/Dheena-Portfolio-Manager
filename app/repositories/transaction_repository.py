"""
Transaction repository.

Owns persistence operations for portfolio transactions.

Database connection creation remains owned by app.database.
The local get_connection import is intentionally retained as a
backward-compatible seam for existing tests and callers that patch
app.repositories.transaction_repository.get_connection.
"""

from contextlib import contextmanager

from app.database import database_connection
from app.database import get_connection


@contextmanager
def _repository_connection():
    """
    Provide a repository connection while preserving backward
    compatibility with callers that patch this module's
    get_connection.

    New application code should use app.database.database_connection
    directly. This adapter exists only at the repository boundary so
    existing tests and integrations can continue patching
    transaction_repository.get_connection.
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


def add_transaction(
    asset,
    asset_type,
    asset_id,
    transaction_type,
    quantity,
    price,
    brokerage,
    dividend,
    bonus,
    transaction_date,
    notes,
):
    with _repository_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO transactions
            (
                asset,
                asset_type,
                asset_id,
                transaction_type,
                quantity,
                price,
                brokerage,
                dividend,
                bonus,
                transaction_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                asset,
                asset_type,
                asset_id,
                transaction_type,
                quantity,
                price,
                brokerage,
                dividend,
                bonus,
                transaction_date,
                notes,
            ),
        )

        return cursor.lastrowid


def get_transactions():
    with _repository_connection() as conn:
        return conn.execute(
            """
            SELECT
                t.*,
                a.name AS asset_name,
                a.symbol
            FROM transactions t
            LEFT JOIN assets a
                ON t.asset_id = a.id
            ORDER BY
                t.transaction_date DESC,
                t.id DESC
            """
        ).fetchall()


def get_transaction(transaction_id):
    with _repository_connection() as conn:
        return conn.execute(
            """
            SELECT *
            FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        ).fetchone()


def get_asset_transactions(asset_id):
    with _repository_connection() as conn:
        return conn.execute(
            """
            SELECT
                t.*,
                a.name AS asset_name,
                a.symbol
            FROM transactions t
            JOIN assets a
                ON t.asset_id = a.id
            WHERE t.asset_id = ?
            ORDER BY
                t.transaction_date DESC,
                t.id DESC
            """,
            (asset_id,),
        ).fetchall()


def get_transactions_with_assets():
    with _repository_connection() as conn:
        return conn.execute(
            """
            SELECT
                t.*,
                a.symbol,
                a.name,
                a.asset_class
            FROM transactions t
            JOIN assets a
                ON t.asset_id = a.id
            ORDER BY
                t.transaction_date,
                t.id
            """
        ).fetchall()


def update_transaction(
    transaction_id,
    asset,
    asset_type,
    asset_id,
    transaction_type,
    quantity,
    price,
    brokerage,
    dividend,
    bonus,
    transaction_date,
    notes,
):
    with _repository_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE transactions
            SET
                asset = ?,
                asset_type = ?,
                asset_id = ?,
                transaction_type = ?,
                quantity = ?,
                price = ?,
                brokerage = ?,
                dividend = ?,
                bonus = ?,
                transaction_date = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                asset,
                asset_type,
                asset_id,
                transaction_type,
                quantity,
                price,
                brokerage,
                dividend,
                bonus,
                transaction_date,
                notes,
                transaction_id,
            ),
        )

        return cursor.rowcount


def delete_transaction(transaction_id):
    with _repository_connection() as conn:
        cursor = conn.execute(
            """
            DELETE
            FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        )

        return cursor.rowcount