import sqlite3
import unittest
from unittest.mock import patch

from app.services import portfolio_service


class GetHoldingTests(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row

        self.conn.execute(
            """
            CREATE TABLE assets (
                id INTEGER PRIMARY KEY,
                symbol TEXT NOT NULL,
                name TEXT NOT NULL,
                asset_class TEXT NOT NULL
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                brokerage REAL DEFAULT 0,
                dividend REAL DEFAULT 0,
                bonus REAL DEFAULT 0,
                transaction_date TEXT NOT NULL
            )
            """
        )

        self.conn.execute(
            "INSERT INTO assets (id, symbol, name, asset_class) VALUES (?, ?, ?, ?)",
            (1, "AAPL", "Apple Inc.", "Stock"),
        )

        self.conn.execute(
            """
            INSERT INTO transactions (
                asset_id,
                transaction_type,
                quantity,
                price,
                brokerage,
                dividend,
                bonus,
                transaction_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (1, "BUY", 10, 100.0, 0.0, 0.0, 0.0, "2024-01-01"),
        )

        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_get_holding_resolves_by_asset_id(self):

        with patch(
            "app.repositories.transaction_repository.get_connection",
            return_value=self.conn,
        ):
            holding = portfolio_service.get_holding(1)

        self.assertIsNotNone(holding)
        self.assertEqual(holding.symbol, "AAPL")
        self.assertAlmostEqual(holding.qty, 10.0)


if __name__ == "__main__":
    unittest.main()
