"""
Holding Domain Model

Represents a single portfolio holding and encapsulates all
business rules related to portfolio calculations.

Cost-basis accounting uses FIFO (First In, First Out):

- Every BUY creates an open FIFO lot.
- Every SELL consumes the oldest open lot(s) first.
- Every BONUS creates zero-cost shares as a new FIFO lot.
- Realized P/L is calculated from the cost of lots consumed by SELL.
- Invested/average cost represent only the currently open lots.
- Lifetime buy cost tracks all BUY transactions, including shares
  that have subsequently been sold.
- DIVIDEND transactions affect income only and do not affect position.

This class intentionally contains no database or Flask logic.
"""


class Holding:
    """Represents a single asset holding using FIFO cost accounting."""

    EPSILON = 1e-9

    def __init__(
        self,
        asset_id: int,
        symbol: str,
        name: str,
        asset_class: str,
    ) -> None:

        # -------------------------------------------------
        # Asset Information
        # -------------------------------------------------

        self.asset_id = asset_id
        self.symbol = symbol
        self.name = name
        self.asset_class = asset_class

        # -------------------------------------------------
        # Holding / FIFO Lots
        # -------------------------------------------------

        self.qty = 0.0
        self.avg = 0.0
        self.invested = 0.0

        self.lots = []

        # -------------------------------------------------
        # Lifetime Cost
        # -------------------------------------------------

        # Total amount spent on all BUY transactions.
        #
        # This does NOT decrease when shares are sold.
        #
        # Example:
        # BUY 10 @ 100  -> 1000
        # BUY 10 @ 200  -> 2000
        # SELL 10       -> lifetime_buy_cost remains 3000
        #
        self.lifetime_buy_cost = 0.0

        # -------------------------------------------------
        # Income / Expenses
        # -------------------------------------------------

        self.brokerage = 0.0
        self.dividend = 0.0
        self.bonus = 0.0

        # -------------------------------------------------
        # Profit & Loss
        # -------------------------------------------------

        self.realized_pl = 0.0
        self.unrealized_pl = 0.0

        # -------------------------------------------------
        # Market
        # -------------------------------------------------

        self.current_price = 0.0
        self.current_value = 0.0

        # -------------------------------------------------
        # Portfolio
        # -------------------------------------------------

        self.allocation = 0.0

    # =====================================================
    # Transactions
    # =====================================================

    def buy(
        self,
        quantity: float,
        price: float,
    ) -> None:
        """
        Process a BUY transaction.

        A BUY creates a new FIFO lot and permanently contributes
        to lifetime_buy_cost.
        """

        if quantity <= 0:
            raise ValueError(
                "Buy quantity must be greater than zero."
            )

        if price < 0:
            raise ValueError(
                "Buy price cannot be negative."
            )

        quantity = float(quantity)
        price = float(price)

        self.lots.append(
            {
                "quantity": quantity,
                "price": price,
            }
        )

        # Lifetime cost must never be reduced by SELL.
        self.lifetime_buy_cost += quantity * price

        self._recalculate_position()

    def sell(
        self,
        quantity: float,
        sell_price: float,
    ) -> None:
        """
        Process a SELL transaction using FIFO cost accounting.

        The oldest open lot is consumed first.

        A single SELL may consume multiple lots.

        SELL does NOT reduce lifetime_buy_cost.
        """

        if quantity <= 0:
            raise ValueError(
                "Sell quantity must be greater than zero."
            )

        if sell_price < 0:
            raise ValueError(
                "Sell price cannot be negative."
            )

        remaining_to_sell = float(quantity)
        sell_price = float(sell_price)

        if remaining_to_sell > self.qty + self.EPSILON:
            raise ValueError(
                "Cannot sell more than current holding."
            )

        realized_pl = 0.0

        while remaining_to_sell > self.EPSILON:

            if not self.lots:
                raise ValueError(
                    "Cannot sell more than current holding."
                )

            lot = self.lots[0]

            consumed = min(
                remaining_to_sell,
                lot["quantity"],
            )

            realized_pl += consumed * (
                sell_price - lot["price"]
            )

            lot["quantity"] -= consumed
            remaining_to_sell -= consumed

            if lot["quantity"] <= self.EPSILON:
                self.lots.pop(0)

        self.realized_pl += realized_pl

        self._recalculate_position()

    def add_bonus_shares(
        self,
        quantity: float,
    ) -> None:
        """
        Process bonus shares as zero-cost shares.

        Bonus shares increase the current quantity but do not
        increase invested capital or lifetime buy cost.

        A zero-cost FIFO lot is created so that:

            quantity increases
            invested remains unchanged
            average cost decreases
            lifetime_buy_cost remains unchanged
        """

        if quantity <= 0:
            raise ValueError(
                "Bonus quantity must be greater than zero."
            )

        quantity = float(quantity)

        self.lots.append(
            {
                "quantity": quantity,
                "price": 0.0,
            }
        )

        self.bonus += quantity

        self._recalculate_position()

    # =====================================================
    # FIFO Position Helpers
    # =====================================================

    def _recalculate_position(self) -> None:
        """Recalculate current position values from open FIFO lots."""

        self.qty = sum(
            lot["quantity"]
            for lot in self.lots
        )

        self.invested = sum(
            lot["quantity"] * lot["price"]
            for lot in self.lots
        )

        if self.qty > self.EPSILON:

            self.avg = (
                self.invested / self.qty
            )

        else:

            self.qty = 0.0
            self.invested = 0.0
            self.avg = 0.0

    # =====================================================
    # Income / Expenses
    # =====================================================

    def add_brokerage(
        self,
        amount: float,
    ) -> None:
        """Accumulate brokerage charges."""

        if amount < 0:
            raise ValueError(
                "Brokerage cannot be negative."
            )

        self.brokerage += float(amount)

    def add_dividend(
        self,
        amount: float,
    ) -> None:
        """
        Record dividend income.

        Dividends do not affect quantity, invested amount,
        average price, lifetime buy cost, or FIFO lots.
        """

        if amount < 0:
            raise ValueError(
                "Dividend cannot be negative."
            )

        self.dividend += float(amount)

    def add_bonus(
        self,
        amount: float,
    ) -> None:
        """
        Record bonus quantity.

        This method is retained as a reporting helper.

        Position-changing bonus transactions should use
        add_bonus_shares(), which both records the bonus and
        creates the zero-cost FIFO lot.
        """

        if amount < 0:
            raise ValueError(
                "Bonus cannot be negative."
            )

        self.bonus += float(amount)

    # =====================================================
    # Market
    # =====================================================

    def update_market_price(
        self,
        price: float,
    ) -> None:
        """Update latest market price."""

        if price is None:
            raise ValueError(
                "Market price cannot be None."
            )

        if price < 0:
            raise ValueError(
                "Market price cannot be negative."
            )

        self.current_price = float(price)

    # =====================================================
    # Calculations
    # =====================================================

    def calculate(
        self,
        total_portfolio_value: float,
    ) -> None:
        """Calculate all derived values."""

        self.current_value = (
            self.qty * self.current_price
        )

        self.unrealized_pl = (
            self.current_value - self.invested
        )

        if total_portfolio_value > 0:

            self.allocation = (
                self.current_value
                / total_portfolio_value
            ) * 100

        else:

            self.allocation = 0.0

    # =====================================================
    # Properties
    # =====================================================

    @property
    def total_pl(self) -> float:
        """
        Total trading profit/loss.

        Dividend income is tracked separately and is not mixed
        into trading P/L.
        """

        return (
            self.realized_pl
            + self.unrealized_pl
        )

    @property
    def return_pct(self) -> float:
        """
        Lifetime return percentage.

        Uses total P/L divided by the total amount spent on
        BUY transactions over the lifetime of the holding.

        This intentionally uses lifetime_buy_cost instead of
        current invested cost because current invested cost
        excludes the cost of shares that have already been sold.
        """

        if self.lifetime_buy_cost <= self.EPSILON:
            return 0.0

        return (
            self.total_pl
            / self.lifetime_buy_cost
        ) * 100

    @property
    def total_buy_cost(self) -> float:
        """
        Backward-compatible alias for lifetime_buy_cost.

        Older code and tests use total_buy_cost.
        The canonical domain attribute is lifetime_buy_cost.
        """
        return self.lifetime_buy_cost
    
    @property
    def is_active(self) -> bool:
        """Return True if the holding currently owns shares."""

        return self.qty > self.EPSILON

    # =====================================================
    # Serialization
    # =====================================================

    def to_dict(self) -> dict:
        """Convert holding into a dictionary suitable for templates/API."""

        return {
            # Asset
            "asset_id": self.asset_id,
            "symbol": self.symbol,
            "name": self.name,
            "type": self.asset_class,

            # Holding
            "qty": round(self.qty, 4),
            "avg": round(self.avg, 2),
            "invested": round(self.invested, 2),

            # Lifetime
            "lifetime_buy_cost": round(
                self.lifetime_buy_cost,
                2,
            ),

            # Market
            "current_price": round(
                self.current_price,
                2,
            ),
            "current": round(
                self.current_value,
                2,
            ),

            # Profit & Loss
            "realized_pl": round(
                self.realized_pl,
                2,
            ),
            "unrealized_pl": round(
                self.unrealized_pl,
                2,
            ),
            "total_pl": round(
                self.total_pl,
                2,
            ),
            "return_pct": round(
                self.return_pct,
                2,
            ),

            # Backward compatibility
            "pl": round(
                self.unrealized_pl,
                2,
            ),

            # Income / Expenses
            "brokerage": round(
                self.brokerage,
                2,
            ),
            "dividend": round(
                self.dividend,
                2,
            ),
            "bonus": round(
                self.bonus,
                2,
            ),

            # Portfolio
            "allocation": round(
                self.allocation,
                2,
            ),
        }