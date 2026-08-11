"""
Asset Repository

Owns persistence operations for assets.

This layer contains SQL/database access only.
Portfolio calculations and transaction-derived positions
belong to the portfolio domain/services.
"""

from app.database import database_connection


class AssetRepository:
    """Persistence operations for portfolio assets."""

    def add(
        self,
        symbol,
        name,
        asset_class,
        exchange,
    ):
        with database_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO assets
                (
                    symbol,
                    name,
                    asset_class,
                    exchange
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    symbol,
                    name,
                    asset_class,
                    exchange,
                ),
            )

            return cursor.lastrowid

    def get_all(self):
        """Return all persisted assets."""

        with database_connection() as conn:
            return conn.execute(
                """
                SELECT *
                FROM assets
                ORDER BY symbol
                """
            ).fetchall()

    def get(self, asset_id):

        with database_connection() as conn:
            return conn.execute(
                """
                SELECT *
                FROM assets
                WHERE id = ?
                """,
                (asset_id,),
            ).fetchone()

    def search(self, search_text):

        with database_connection() as conn:
            return conn.execute(
                """
                SELECT *
                FROM assets
                WHERE
                    symbol LIKE ?
                    OR name LIKE ?
                ORDER BY symbol
                LIMIT 10
                """,
                (
                    f"%{search_text}%",
                    f"%{search_text}%",
                ),
            ).fetchall()

    def get_summary(self):

        with database_connection() as conn:
            return conn.execute(
                """
                SELECT
                    COUNT(*) AS assets,

                    SUM(
                        CASE
                            WHEN asset_class = 'Stock'
                            THEN 1
                            ELSE 0
                        END
                    ) AS stocks,

                    SUM(
                        CASE
                            WHEN asset_class = 'ETF'
                            THEN 1
                            ELSE 0
                        END
                    ) AS etfs,

                    SUM(
                        CASE
                            WHEN asset_class = 'Mutual Fund'
                            THEN 1
                            ELSE 0
                        END
                    ) AS mutual_funds

                FROM assets
                """
            ).fetchone()