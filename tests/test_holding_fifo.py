import unittest

from app.models.holding import Holding


class HoldingFIFOTests(unittest.TestCase):

    def make_holding(self):
        return Holding(
            asset_id=1,
            symbol="DMY",
            name="dummy",
            asset_class="Stock",
        )

    def test_fifo_partial_sell(self):
        holding = self.make_holding()

        holding.buy(10, 100)
        holding.buy(10, 120)
        holding.sell(5, 150)

        self.assertAlmostEqual(
            holding.qty,
            15.0,
        )

        self.assertAlmostEqual(
            holding.invested,
            1700.0,
        )

        self.assertAlmostEqual(
            holding.avg,
            113.3333333333,
        )

        self.assertAlmostEqual(
            holding.realized_pl,
            250.0,
        )

        self.assertAlmostEqual(
            holding.total_buy_cost,
            2200.0,
        )

        holding.update_market_price(120)
        holding.calculate(1800)

        self.assertAlmostEqual(
            holding.current_value,
            1800.0,
        )

        self.assertAlmostEqual(
            holding.unrealized_pl,
            100.0,
        )

        self.assertAlmostEqual(
            holding.total_pl,
            350.0,
        )

        self.assertAlmostEqual(
            holding.return_pct,
            (350 / 2200) * 100,
        )

    def test_fifo_sell_consumes_multiple_lots(self):
        holding = self.make_holding()

        holding.buy(2, 100)
        holding.buy(3, 200)
        holding.sell(4, 300)

        self.assertAlmostEqual(
            holding.realized_pl,
            600.0,
        )

        self.assertAlmostEqual(
            holding.qty,
            1.0,
        )

        self.assertAlmostEqual(
            holding.invested,
            200.0,
        )

        self.assertAlmostEqual(
            holding.avg,
            200.0,
        )

        self.assertAlmostEqual(
            holding.total_buy_cost,
            800.0,
        )

        holding.update_market_price(300)
        holding.calculate(300)

        self.assertAlmostEqual(
            holding.unrealized_pl,
            100.0,
        )

        self.assertAlmostEqual(
            holding.total_pl,
            700.0,
        )

        self.assertAlmostEqual(
            holding.return_pct,
            (700 / 800) * 100,
        )

    def test_beml_transaction_sequence_uses_fifo_order(self):
        holding = self.make_holding()

        holding.buy(10, 1000)
        holding.buy(1, 100)
        holding.sell(1, 100)

        self.assertAlmostEqual(
            holding.realized_pl,
            -900.0,
        )

        self.assertAlmostEqual(
            holding.qty,
            10.0,
        )

        self.assertAlmostEqual(
            holding.invested,
            9100.0,
        )

        self.assertAlmostEqual(
            holding.avg,
            910.0,
        )

        self.assertAlmostEqual(
            holding.total_buy_cost,
            10100.0,
        )

        holding.update_market_price(1000)
        holding.calculate(10000)

        self.assertAlmostEqual(
            holding.unrealized_pl,
            900.0,
        )

        self.assertAlmostEqual(
            holding.total_pl,
            0.0,
        )

        self.assertAlmostEqual(
            holding.return_pct,
            0.0,
        )

    def test_fifo_sell_entire_position(self):
        holding = self.make_holding()

        holding.buy(1, 100)
        holding.sell(1, 150)

        self.assertEqual(
            holding.qty,
            0.0,
        )

        self.assertEqual(
            holding.invested,
            0.0,
        )

        self.assertEqual(
            holding.avg,
            0.0,
        )

        self.assertAlmostEqual(
            holding.realized_pl,
            50.0,
        )

        self.assertAlmostEqual(
            holding.total_buy_cost,
            100.0,
        )

        self.assertAlmostEqual(
            holding.return_pct,
            50.0,
        )

        self.assertFalse(
            holding.is_active
        )

    def test_sell_more_than_position_is_rejected(self):
        holding = self.make_holding()

        holding.buy(5, 100)

        with self.assertRaises(ValueError):
            holding.sell(6, 150)

    def test_bonus_does_not_increase_buy_cost(self):
        holding = self.make_holding()

        holding.buy(10, 100)
        holding.add_bonus_shares(5)

        self.assertAlmostEqual(
            holding.qty,
            15.0,
        )

        self.assertAlmostEqual(
            holding.invested,
            1000.0,
        )

        self.assertAlmostEqual(
            holding.total_buy_cost,
            1000.0,
        )

        self.assertAlmostEqual(
            holding.avg,
            1000 / 15,
        )

    def test_dividend_does_not_change_buy_cost(self):
        holding = self.make_holding()

        holding.buy(10, 100)
        holding.add_dividend(50)

        self.assertAlmostEqual(
            holding.qty,
            10.0,
        )

        self.assertAlmostEqual(
            holding.invested,
            1000.0,
        )

        self.assertAlmostEqual(
            holding.total_buy_cost,
            1000.0,
        )

        self.assertAlmostEqual(
            holding.dividend,
            50.0,
        )

if __name__ == "__main__":
    unittest.main()