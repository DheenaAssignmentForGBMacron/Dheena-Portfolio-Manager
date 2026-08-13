"""
Portfolio Engine

Builds the current portfolio state from persisted transactions.

Responsibilities:
- Replay transactions chronologically.
- Build Holding domain objects.
- Apply transaction effects.
- Fetch current market prices.
- Calculate holding-level derived values.
- Build portfolio-level aggregates.

The engine contains no Flask or database connection management.
"""

from app.models.holding import Holding
from app.repositories.transaction_repository import (
    get_transactions_with_assets,
)
from app.services.price_service import get_price


SUPPORTED_TRANSACTION_TYPES = frozenset({
    "BUY",
    "SELL",
    "DIVIDEND",
    "BONUS",
})


class PortfolioEngine:
    """Build and calculate the current portfolio state."""

    def __init__(self):
        self.holdings = {}

    def process(self):
        """
        Build the current and historical portfolio state.

        Current holdings contain only assets with an open position.
        Historical holdings contain assets whose position has been
        completely sold.

        All transactions are replayed before the split so lifetime
        metrics such as realized P/L and total buy cost are preserved.
        """

        self.holdings = {}

        rows = self._load_transactions()

        self._build_holdings(rows)

        # Calculate against the complete transaction-derived state
        # before separating current and historical holdings.
        self._update_live_prices()

        self._calculate_holdings()

        current_holdings = {
            asset_id: holding
            for asset_id, holding in self.holdings.items()
            if holding.qty > 0
        }

        historical_holdings = {
            asset_id: holding
            for asset_id, holding in self.holdings.items()
            if holding.qty <= 0
        }

        self.holdings = current_holdings

        return {
            "holdings": self.holdings,
            "historical_holdings": historical_holdings,
            "summary": self._build_summary(
                historical_holdings=historical_holdings
            ),
        }

    def _load_transactions(self):
        """Load transactions through the repository layer."""

        return get_transactions_with_assets()

    def _get_or_create_holding(self, row):
        """Return the holding for an asset."""

        asset_id = row["asset_id"]

        if asset_id not in self.holdings:
            self.holdings[asset_id] = Holding(
                asset_id=row["asset_id"],
                symbol=row["symbol"],
                name=row["name"],
                asset_class=row["asset_class"],
            )

        return self.holdings[asset_id]

    def _build_holdings(self, rows):
        """Replay transactions into holdings."""

        for row in rows:
            transaction_type = row["transaction_type"]

            if transaction_type not in SUPPORTED_TRANSACTION_TYPES:
                raise ValueError(
                    f"Unsupported transaction type: {transaction_type}"
                )

            holding = self._get_or_create_holding(row)

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

            if transaction_type == "BUY":
                holding.buy(
                    quantity,
                    price,
                )

            elif transaction_type == "SELL":
                holding.sell(
                    quantity,
                    price,
                )

            elif transaction_type == "DIVIDEND":
                holding.add_dividend(
                    dividend
                )

            elif transaction_type == "BONUS":
                holding.add_bonus_shares(
                    bonus
                )

            holding.add_brokerage(
                brokerage
            )

    def _update_live_prices(self):
        """Update holdings with current market prices."""

        for holding in self.holdings.values():

            market_price = get_price(
                holding.symbol
            )

            if market_price is not None:
                holding.update_market_price(
                    market_price
                )

    def _calculate_holdings(self):
        """Calculate holding-level derived values."""

        total_current_value = sum(
            holding.qty * holding.current_price
            for holding in self.holdings.values()
        )

        for holding in self.holdings.values():
            holding.calculate(
                total_current_value
            )

    def _build_summary(self, historical_holdings=None):
        """Build portfolio-level aggregate values."""

        historical_holdings = (
            historical_holdings
            if historical_holdings is not None
            else {}
        )

        all_holdings = list(self.holdings.values()) + list(
            historical_holdings.values()
        )

        summary = {
            "invested": 0.0,
            "current": 0.0,
            "realized_pl": 0.0,
            "unrealized_pl": 0.0,
            "total_pl": 0.0,
            "total_buy_cost": 0.0,
            "return_pct": 0.0,
            "brokerage": 0.0,
            "dividend": 0.0,
            "bonus": 0.0,
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

        # -----------------------------------------------------
        # Current portfolio values
        # -----------------------------------------------------

        for holding in self.holdings.values():

            summary["invested"] += holding.invested

            summary["current"] += holding.current_value

            summary["unrealized_pl"] += holding.unrealized_pl

            asset_type = (
                holding.asset_class.lower()
                if holding.asset_class
                else ""
            )

            counter_key = asset_counter.get(asset_type)

            if counter_key:
                summary[counter_key] += 1

        # -----------------------------------------------------
        # Lifetime portfolio values
        # -----------------------------------------------------

        for holding in all_holdings:

            summary["realized_pl"] += holding.realized_pl

            summary["total_pl"] += holding.total_pl

            summary["total_buy_cost"] += holding.lifetime_buy_cost

            summary["brokerage"] += holding.brokerage

            summary["dividend"] += holding.dividend

            summary["bonus"] += holding.bonus

        # -----------------------------------------------------
        # Portfolio Return
        # -----------------------------------------------------

        if summary["total_buy_cost"] > 0:
            summary["return_pct"] = (
                summary["total_pl"]
                / summary["total_buy_cost"]
            ) * 100

        # -----------------------------------------------------
        # Round Financial Values
        # -----------------------------------------------------

        financial_keys = (
            "invested",
            "current",
            "realized_pl",
            "unrealized_pl",
            "total_pl",
            "total_buy_cost",
            "return_pct",
            "brokerage",
            "dividend",
            "bonus",
        )

        for key in financial_keys:
            summary[key] = round(
                summary[key],
                2,
            )

        return summary