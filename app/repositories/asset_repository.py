from app.database import get_connection


class AssetRepository:

    # =====================================================
    # Create
    # =====================================================

    def add(
        self,
        symbol,
        name,
        asset_class,
        exchange,
    ):

        conn = get_connection()

        conn.execute(
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

        conn.commit()
        conn.close()

    # =====================================================
    # Read
    # =====================================================

    def get_all(self):

        conn = get_connection()

        rows = conn.execute(
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

            GROUP BY
                a.id

            ORDER BY
                a.symbol
            """
        ).fetchall()

        conn.close()

        return rows

    def get(self, asset_id):

        conn = get_connection()

        row = conn.execute(
            """
            SELECT *
            FROM assets
            WHERE id = ?
            """,
            (asset_id,),
        ).fetchone()

        conn.close()

        return row

    def search(self, search_text):

        conn = get_connection()

        rows = conn.execute(
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

        conn.close()

        return rows

    # =====================================================
    # Summary
    # =====================================================

    def get_summary(self):

        conn = get_connection()

        summary = conn.execute(
            """
            SELECT

                COUNT(*) AS assets,

                SUM(
                    CASE
                        WHEN asset_class='Stock'
                        THEN 1
                        ELSE 0
                    END
                ) AS stocks,

                SUM(
                    CASE
                        WHEN asset_class='ETF'
                        THEN 1
                        ELSE 0
                    END
                ) AS etfs,

                SUM(
                    CASE
                        WHEN asset_class='Mutual Fund'
                        THEN 1
                        ELSE 0
                    END
                ) AS mutual_funds

            FROM assets
            """
        ).fetchone()

        conn.close()

        return summary

    # =====================================================
    # Seed
    # =====================================================

    def seed(self, assets):

        conn = get_connection()

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

        conn.commit()
        conn.close()