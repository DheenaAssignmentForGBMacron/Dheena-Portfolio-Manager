import sqlite3
import unittest
from unittest.mock import patch

from app.services import snapshot_service


class SnapshotServiceTests(unittest.TestCase):

    def setUp(self):

        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row

        self.conn.execute(
            """
            CREATE TABLE portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date DATE NOT NULL UNIQUE,
                invested REAL NOT NULL,
                current REAL NOT NULL,
                realized_pl REAL NOT NULL,
                unrealized_pl REAL NOT NULL,
                total_pl REAL NOT NULL,
                return_pct REAL NOT NULL,
                brokerage REAL NOT NULL,
                dividend REAL NOT NULL,
                bonus REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE asset_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date DATE NOT NULL,
                asset_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                average_price REAL NOT NULL,
                market_price REAL NOT NULL,
                invested REAL NOT NULL,
                current REAL NOT NULL,
                realized_pl REAL NOT NULL,
                unrealized_pl REAL NOT NULL,
                total_pl REAL NOT NULL,
                allocation REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(snapshot_date, asset_id)
            )
            """
        )

        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def _portfolio(self):
        return {
            "summary": {
                "invested": 10000.0,
                "current": 12000.0,
                "realized_pl": 500.0,
                "unrealized_pl": 1500.0,
                "total_pl": 2000.0,
                "return_pct": 20.0,
                "brokerage": 100.0,
                "dividend": 50.0,
                "bonus": 2.0,
            },
            "holdings": [
                {
                    "asset_id": 1,
                    "qty": 10.0,
                    "avg": 1000.0,
                    "current_price": 1200.0,
                    "invested": 10000.0,
                    "current": 12000.0,
                    "realized_pl": 500.0,
                    "unrealized_pl": 1500.0,
                    "total_pl": 2000.0,
                    "allocation": 100.0,
                }
            ],
        }

    def test_snapshot_exists_returns_false_when_missing(self):

        with patch(
            "app.services.snapshot_service.database_connection",
            self._connection_context,
        ):
            self.assertFalse(
                snapshot_service.snapshot_exists(
                    "2026-01-01"
                )
            )

    def test_save_snapshot_persists_portfolio_and_assets(self):

        with patch(
            "app.services.snapshot_service.get_portfolio",
            return_value=self._portfolio(),
        ), patch(
            "app.services.snapshot_service.database_connection",
            self._connection_context,
        ):
            snapshot_service.save_snapshot(
                "2026-01-01"
            )

        portfolio = self.conn.execute(
            """
            SELECT *
            FROM portfolio_snapshots
            """
        ).fetchone()

        asset = self.conn.execute(
            """
            SELECT *
            FROM asset_snapshots
            """
        ).fetchone()

        self.assertIsNotNone(portfolio)
        self.assertIsNotNone(asset)

        self.assertEqual(
            portfolio["snapshot_date"],
            "2026-01-01",
        )

        self.assertAlmostEqual(
            portfolio["current"],
            12000.0,
        )

        self.assertAlmostEqual(
            portfolio["realized_pl"],
            500.0,
        )

        self.assertAlmostEqual(
            portfolio["unrealized_pl"],
            1500.0,
        )

        self.assertAlmostEqual(
            portfolio["total_pl"],
            2000.0,
        )

        self.assertAlmostEqual(
            asset["total_pl"],
            2000.0,
        )

    def test_duplicate_snapshot_does_not_create_second_record(self):

        with patch(
            "app.services.snapshot_service.get_portfolio",
            return_value=self._portfolio(),
        ), patch(
            "app.services.snapshot_service.database_connection",
            self._connection_context,
        ):
            snapshot_service.save_snapshot(
                "2026-01-01"
            )

            snapshot_service.save_snapshot(
                "2026-01-01"
            )

        portfolio_count = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM portfolio_snapshots
            """
        ).fetchone()[0]

        asset_count = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM asset_snapshots
            """
        ).fetchone()[0]

        self.assertEqual(
            portfolio_count,
            1,
        )

        self.assertEqual(
            asset_count,
            1,
        )

    def test_get_snapshots_preserves_historical_values(self):

        self.conn.execute(
            """
            INSERT INTO portfolio_snapshots
            (
                snapshot_date,
                invested,
                current,
                realized_pl,
                unrealized_pl,
                total_pl,
                return_pct,
                brokerage,
                dividend,
                bonus
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "2026-01-01",
                10000,
                11000,
                0,
                1000,
                1000,
                10,
                50,
                0,
                0,
            ),
        )

        self.conn.commit()

        with patch(
            "app.services.snapshot_service.database_connection",
            self._connection_context,
        ):
            snapshots = snapshot_service.get_snapshots()

        self.assertEqual(
            len(snapshots),
            1,
        )

        self.assertEqual(
            snapshots[0]["snapshot_date"],
            "2026-01-01",
        )

        self.assertAlmostEqual(
            snapshots[0]["current_value"],
            11000,
        )

        self.assertAlmostEqual(
            snapshots[0]["profit"],
            1000,
        )

    def test_get_asset_snapshots_can_filter_by_asset(self):

        self.conn.execute(
            """
            INSERT INTO asset_snapshots
            (
                snapshot_date,
                asset_id,
                quantity,
                average_price,
                market_price,
                invested,
                current,
                realized_pl,
                unrealized_pl,
                total_pl,
                allocation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "2026-01-01",
                1,
                10,
                100,
                120,
                1000,
                1200,
                0,
                200,
                200,
                100,
            ),
        )

        self.conn.execute(
            """
            INSERT INTO asset_snapshots
            (
                snapshot_date,
                asset_id,
                quantity,
                average_price,
                market_price,
                invested,
                current,
                realized_pl,
                unrealized_pl,
                total_pl,
                allocation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "2026-01-01",
                2,
                5,
                200,
                220,
                1000,
                1100,
                0,
                100,
                100,
                50,
            ),
        )

        self.conn.commit()

        with patch(
            "app.services.snapshot_service.database_connection",
            self._connection_context,
        ):
            snapshots = (
                snapshot_service.get_asset_snapshots(
                    asset_id=1
                )
            )

        self.assertEqual(
            len(snapshots),
            1,
        )

        self.assertEqual(
            snapshots[0]["asset_id"],
            1,
        )

    def _connection_context(self):
        class ConnectionContext:

            def __enter__(_,):
                return self.conn

            def __exit__(_, exc_type, exc, tb):
                if exc_type is None:
                    self.conn.commit()
                else:
                    self.conn.rollback()

        return ConnectionContext()


if __name__ == "__main__":
    unittest.main()