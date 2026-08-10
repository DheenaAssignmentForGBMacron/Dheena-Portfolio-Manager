"""
Portfolio Engine

Builds the current portfolio from persisted transactions.

Responsibilities:
- Replay transactions in chronological order.
- Build Holding domain objects.
- Fetch current market prices.
- Calculate portfolio-level derived values.
- Build the portfolio summary.

The engine contains no Flask logic and does not own
database connections.
"""

from app.models.holding import Holding
from app.repositories.transaction_repository import (
    get_transactions_with_assets,
)
from app.services.price_service import get_price


class PortfolioEngine:
    """Build and calculate the current portfolio state."""

    def __init__(self):
        self.holdings = {}

    # =====================================================
    # Main Processor
    # =====================================================

    def process(self):
        """
        Build the portfolio from the latest transaction data.

        The engine is intentionally reusable. Every call starts
        from a clean holding state so repeated calls cannot
        accumulate transactions or P/L from previous runs.
        """

        self.holdings = {}

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
    # Repository
    # =====================================================

    def _load_transactions(self):
        """
        Load portfolio transactions through the repository.

        PortfolioEngine is responsible for portfolio calculations,
        not database access.
        """

        return get_transactions_with_assets()

    # =====================================================
    # Holdings
    # =====================================================

    def _build_holdings(self, rows):
        """Replay transactions and build current holdings."""

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

            transaction_type = row["transaction_type"]

            quantity = float(
                row["quantity"] or 0
            )

            price = float(
                row["price"] or 0
            )

            brokerage = float(
                row["brokerage"] or 0
            )

            dividend = float(
                row["dividend"] or 0
            )

            bonus = float(
                row["bonus"] or 0
            )

            # =================================================
            # BUY
            # =================================================

            if transaction_type == "BUY":

                holding.buy(
                    quantity,
                    price,
                )

            # =================================================
            # SELL
            # =================================================

            elif transaction_type == "SELL":

                holding.sell(
                    quantity,
                    price,
                )

            # =================================================
            # DIVIDEND
            # =================================================

            elif transaction_type == "DIVIDEND":

                holding.add_dividend(
                    dividend
                )

            # =================================================
            # BONUS
            # =================================================

            elif transaction_type == "BONUS":

                holding.add_bonus_shares(
                    bonus
                )

            # =================================================
            # Unsupported
            # =================================================

            else:

                continue

            # =================================================
            # Transaction-level Brokerage
            # =================================================

            holding.add_brokerage(
                brokerage
            )

    # =====================================================
    # Live Prices
    # =====================================================

    def _update_live_prices(self):
        """Update every holding with its latest market price."""

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
        """Calculate derived values for every holding."""

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
        """Build portfolio-level aggregate values."""

        summary = {
            "invested": 0.0,
            "current": 0.0,

            "realized_pl": 0.0,
            "unrealized_pl": 0.0,
            "total_pl": 0.0,
            "return_pct": 0.0,

            "brokerage": 0.0,
            "dividend": 0.0,
            "bonus": 0.0,

            "holdings_count": len(
                self.holdings
            ),

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

        # =================================================
        # Aggregate Holdings
        # =================================================

        for holding in self.holdings.values():

            summary["invested"] += holding.invested

            summary["current"] += holding.current_value

            summary["realized_pl"] += holding.realized_pl

            summary["unrealized_pl"] += holding.unrealized_pl

            summary["total_pl"] += holding.total_pl

            summary["brokerage"] += holding.brokerage

            summary["dividend"] += holding.dividend

            summary["bonus"] += holding.bonus

            asset_type = (
                holding.asset_class.lower()
                if holding.asset_class
                else ""
            )

            if asset_type in asset_counter:

                summary[
                    asset_counter[asset_type]
                ] += 1

        # =================================================
        # Portfolio Return
        # =================================================

        if summary["invested"] > 0:

            summary["return_pct"] = (
                summary["total_pl"]
                / summary["invested"]
            ) * 100

        # =================================================
        # Round Financial Values
        # =================================================

        for key in (
            "invested",
            "current",
            "realized_pl",
            "unrealized_pl",
            "total_pl",
            "return_pct",
            "brokerage",
            "dividend",
            "bonus",
        ):

            summary[key] = round(
                summary[key],
                2,
            )

        return summary