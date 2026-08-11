from app.database import database_connection


class AssetRepository:

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

        with database_connection() as conn:
            return conn.execute(
                """
                SELECT
                    a.*,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN t.transaction_type = 'BUY'
                                    THEN t.quantity

                                WHEN t.transaction_type = 'SELL'
                                    THEN -t.quantity

                                ELSE 0
                            END
                        ),
                        0
                    ) AS holdings

                FROM assets a

                LEFT JOIN transactions t
                    ON t.asset_id = a.id

                GROUP BY a.id

                ORDER BY a.symbol
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

    def seed(self, assets):

        with database_connection() as conn:
            conn.executemany(
                """
                INSERT OR IGNORE INTO assets
                (
                    symbol,
                    name,
                    asset_class,
                    exchange
                )
                VALUES (?, ?, ?, ?)
                """,
                assets,
            )