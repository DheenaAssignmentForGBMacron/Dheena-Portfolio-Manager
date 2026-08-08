from app.database import get_connection
from app.models.holding import Holding
from app.services.price_service import get_price


class PortfolioEngine:

    def __init__(self):
        self.holdings = {}

    # =====================================================
    # Main Processor
    # =====================================================

    def process(self):

        rows = self._load_transactions()

        self._build_holdings(rows)

        self._update_live_prices()

        self._calculate_holdings()

        summary = self._build_summary()

        return {
            "holdings": self.holdings,
            "summary": summary,
        }

    # =====================================================
    # Database
    # =====================================================

    def _load_transactions(self):

        conn = get_connection()

        rows = conn.execute("""
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
        """).fetchall()

        conn.close()

        return rows

    # =====================================================
    # Holdings
    # =====================================================

    def _build_holdings(self, rows):

        for row in rows:

            asset_id = row["asset_id"]

            if asset_id not in self.holdings:

                self.holdings[asset_id] = Holding(
                    asset_id=row["asset_id"],
                    symbol=row["symbol"],
                    name=row["name"],
                    asset_class=row["asset_class"],
                )

            holding = self.holdings[asset_id]

            qty = float(row["quantity"])
            price = float(row["price"])

            if row["transaction_type"] == "BUY":

                holding.buy(
                    qty,
                    price,
                )

            elif row["transaction_type"] == "SELL":

                holding.sell(
                    qty,
                    price,
                )

            else:

                # Ignore unsupported transaction types
                # such as DIVIDEND for position accounting.
                continue

            holding.add_brokerage(
                float(row["brokerage"] or 0)
            )

            holding.add_dividend(
                float(row["dividend"] or 0)
            )

            holding.add_bonus(
                float(row["bonus"] or 0)
            )

    # =====================================================
    # Live Prices
    # =====================================================

    def _update_live_prices(self):

        for holding in self.holdings.values():

            market_price = get_price(
                holding.symbol
            )

            if market_price is not None:

                holding.update_market_price(
                    market_price
                )

    # =====================================================
    # Calculations
    # =====================================================

    def _calculate_holdings(self):

        total_current_value = sum(

            holding.qty * holding.current_price

            for holding in self.holdings.values()

        )

        for holding in self.holdings.values():

            holding.calculate(
                total_current_value
            )

    # =====================================================
    # Summary
    # =====================================================

    def _build_summary(self):

        summary = {

            # -------------------------------------------------
            # Portfolio Value
            # -------------------------------------------------

            "invested": 0.0,
            "current": 0.0,

            # -------------------------------------------------
            # Profit & Loss
            # -------------------------------------------------

            "realized_pl": 0.0,
            "unrealized_pl": 0.0,
            "total_pl": 0.0,
            "return_pct": 0.0,

            # -------------------------------------------------
            # Income / Expenses
            # -------------------------------------------------

            "brokerage": 0.0,
            "dividend": 0.0,
            "bonus": 0.0,

            # -------------------------------------------------
            # Holding Counts
            # -------------------------------------------------

            "holdings_count": len(self.holdings),

            "stock_count": 0,
            "mf_count": 0,
            "etf_count": 0,
            "crypto_count": 0,
            "gold_count": 0,
        }

        asset_counter = {

            "stock": "stock_count",
            "mutual fund": "mf_count",
            "etf": "etf_count",
            "crypto": "crypto_count",
            "gold": "gold_count",
        }

        # =====================================================
        # Aggregate Holdings
        # =====================================================

        for holding in self.holdings.values():

            summary["invested"] += (
                holding.invested
            )

            summary["current"] += (
                holding.current_value
            )

            summary["realized_pl"] += (
                holding.realized_pl
            )

            summary["unrealized_pl"] += (
                holding.unrealized_pl
            )

            summary["total_pl"] += (
                holding.total_pl
            )

            summary["brokerage"] += (
                holding.brokerage
            )

            summary["dividend"] += (
                holding.dividend
            )

            summary["bonus"] += (
                holding.bonus
            )

            asset_type = (
                holding.asset_class.lower()
                if holding.asset_class
                else ""
            )

            if asset_type in asset_counter:

                summary[
                    asset_counter[asset_type]
                ] += 1

        # =====================================================
        # Portfolio Return
        # =====================================================

        if summary["invested"] > 0:

            summary["return_pct"] = (

                summary["total_pl"]
                / summary["invested"]

            ) * 100

        # =====================================================
        # Round Financial Values
        # =====================================================

        summary["invested"] = round(
            summary["invested"],
            2,
        )

        summary["current"] = round(
            summary["current"],
            2,
        )

        summary["realized_pl"] = round(
            summary["realized_pl"],
            2,
        )

        summary["unrealized_pl"] = round(
            summary["unrealized_pl"],
            2,
        )

        summary["total_pl"] = round(
            summary["total_pl"],
            2,
        )

        summary["return_pct"] = round(
            summary["return_pct"],
            2,
        )

        summary["brokerage"] = round(
            summary["brokerage"],
            2,
        )

        summary["dividend"] = round(
            summary["dividend"],
            2,
        )

        summary["bonus"] = round(
            summary["bonus"],
            2,
        )

        return summary