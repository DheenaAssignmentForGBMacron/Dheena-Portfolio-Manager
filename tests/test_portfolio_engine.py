import unittest
from unittest.mock import patch

from app.services.portfolio_engine import PortfolioEngine


class PortfolioEngineTests(unittest.TestCase):

    def make_row(
        self,
        transaction_id,
        asset_id,
        symbol,
        name,
        asset_class,
        transaction_type,
        quantity,
        price,
        brokerage=0,
        dividend=0,
        bonus=0,
        transaction_date="2026-01-01",
    ):
        return {
            "id": transaction_id,
            "asset_id": asset_id,
            "symbol": symbol,
            "name": name,
            "asset_class": asset_class,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "price": price,
            "brokerage": brokerage,
            "dividend": dividend,
            "bonus": bonus,
            "transaction_date": transaction_date,
        }

    # =====================================================
    # Portfolio Processing
    # =====================================================

    @patch("app.services.portfolio_engine.get_price")
    @patch("app.services.portfolio_engine.get_transactions_with_assets")
    def test_process_builds_correct_portfolio(
        self,
        mock_get_transactions,
        mock_get_price,
    ):
        mock_get_transactions.return_value = [

            # BUY 5 @ 100
            self.make_row(
                transaction_id=1,
                asset_id=1,
                symbol="ABC",
                name="ABC Ltd",
                asset_class="Stock",
                transaction_type="BUY",
                quantity=5,
                price=100,
            ),

            # BUY 5 @ 200
            self.make_row(
                transaction_id=2,
                asset_id=1,
                symbol="ABC",
                name="ABC Ltd",
                asset_class="Stock",
                transaction_type="BUY",
                quantity=5,
                price=200,
            ),

            # SELL 3 @ 300
            # FIFO consumes 3 shares from the ₹100 lot.
            self.make_row(
                transaction_id=3,
                asset_id=1,
                symbol="ABC",
                name="ABC Ltd",
                asset_class="Stock",
                transaction_type="SELL",
                quantity=3,
                price=300,
            ),
        ]

        mock_get_price.return_value = 240

        engine = PortfolioEngine()

        result = engine.process()

        holdings = result["holdings"]
        summary = result["summary"]

        holding = holdings[1]

        # -------------------------------------------------
        # Position
        # -------------------------------------------------

        self.assertAlmostEqual(holding.qty, 7.0)
        self.assertAlmostEqual(holding.invested, 1200.0)
        self.assertAlmostEqual(holding.avg, 1200 / 7)

        self.assertAlmostEqual(
            holding.realized_pl,
            600.0,
        )

        self.assertAlmostEqual(
            holding.current_value,
            1680.0,
        )

        self.assertAlmostEqual(
            holding.unrealized_pl,
            480.0,
        )

        self.assertAlmostEqual(
            holding.total_pl,
            1080.0,
        )

        self.assertAlmostEqual(
            summary["invested"],
            1200.0,
        )

        self.assertAlmostEqual(
            summary["current"],
            1680.0,
        )

        self.assertAlmostEqual(
            summary["realized_pl"],
            600.0,
        )

        self.assertAlmostEqual(
            summary["unrealized_pl"],
            480.0,
        )

        self.assertAlmostEqual(
            summary["total_pl"],
            1080.0,
        )

        self.assertAlmostEqual(
            summary["return_pct"],
            90.0,
        )
    # =====================================================
    # Multiple Assets
    # =====================================================

    @patch("app.services.portfolio_engine.get_price")
    @patch("app.services.portfolio_engine.get_transactions_with_assets")
    def test_process_keeps_assets_separate(
        self,
        mock_get_transactions,
        mock_get_price,
    ):
        mock_get_transactions.return_value = [

            self.make_row(
                transaction_id=1,
                asset_id=1,
                symbol="ABC",
                name="ABC Ltd",
                asset_class="Stock",
                transaction_type="BUY",
                quantity=10,
                price=100,
            ),

            self.make_row(
                transaction_id=2,
                asset_id=2,
                symbol="XYZ",
                name="XYZ Ltd",
                asset_class="ETF",
                transaction_type="BUY",
                quantity=5,
                price=200,
            ),
        ]

        def price_side_effect(symbol):
            if symbol == "ABC":
                return 120

            if symbol == "XYZ":
                return 250

            return None

        mock_get_price.side_effect = price_side_effect

        engine = PortfolioEngine()

        result = engine.process()

        holdings = result["holdings"]

        self.assertEqual(
            len(holdings),
            2,
        )

        abc = holdings[1]
        xyz = holdings[2]

        # ABC
        self.assertAlmostEqual(
            abc.qty,
            10.0,
        )

        self.assertAlmostEqual(
            abc.invested,
            1000.0,
        )

        self.assertAlmostEqual(
            abc.current_value,
            1200.0,
        )

        self.assertAlmostEqual(
            abc.unrealized_pl,
            200.0,
        )

        # XYZ
        self.assertAlmostEqual(
            xyz.qty,
            5.0,
        )

        self.assertAlmostEqual(
            xyz.invested,
            1000.0,
        )

        self.assertAlmostEqual(
            xyz.current_value,
            1250.0,
        )

        self.assertAlmostEqual(
            xyz.unrealized_pl,
            250.0,
        )

    # =====================================================
    # Unsupported Transactions
    # =====================================================

    @patch("app.services.portfolio_engine.get_price")
    @patch("app.services.portfolio_engine.get_transactions_with_assets")
    def test_unsupported_transaction_does_not_change_position(
        self,
        mock_get_transactions,
        mock_get_price,
    ):
        mock_get_transactions.return_value = [

            self.make_row(
                transaction_id=1,
                asset_id=1,
                symbol="ABC",
                name="ABC Ltd",
                asset_class="Stock",
                transaction_type="BUY",
                quantity=10,
                price=100,
            ),

            self.make_row(
                transaction_id=2,
                asset_id=1,
                symbol="ABC",
                name="ABC Ltd",
                asset_class="Stock",
                transaction_type="DIVIDEND",
                quantity=0,
                price=0,
                dividend=50,
            ),
        ]

        mock_get_price.return_value = 120

        engine = PortfolioEngine()

        result = engine.process()

        holding = result["holdings"][1]

        # -------------------------------------------------
        # Position must remain unchanged
        # -------------------------------------------------

        self.assertAlmostEqual(
            holding.qty,
            10.0,
        )

        self.assertAlmostEqual(
            holding.invested,
            1000.0,
        )

        self.assertAlmostEqual(
            holding.avg,
            100.0,
        )

        # -------------------------------------------------
        # Dividend should still be recorded
        # -------------------------------------------------

        self.assertAlmostEqual(
            holding.dividend,
            0.0,
        )


if __name__ == "__main__":
    unittest.main()