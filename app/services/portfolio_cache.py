"""
Portfolio Cache Service

Caches the calculated portfolio in memory.

The portfolio is derived data. It is built by PortfolioEngine
from transactions and live market prices, then retained until
the underlying transaction data changes.

This class contains no database logic.
"""

from app.services.portfolio_engine import PortfolioEngine


class PortfolioCache:
    """In-memory cache for the calculated portfolio."""

    def __init__(self) -> None:
        self._portfolio = None

    # =====================================================
    # Get Portfolio
    # =====================================================

    def get_portfolio(self):
        """
        Return the cached portfolio.

        If no cached portfolio exists, build it through
        PortfolioEngine and cache the result.
        """

        if self._portfolio is None:
            self._portfolio = PortfolioEngine().process()

        return self._portfolio

    # =====================================================
    # Invalidate
    # =====================================================

    def invalidate(self) -> None:
        """
        Clear the cached portfolio.

        The next call to get_portfolio() will rebuild the
        portfolio from the latest transaction data and
        latest available market prices.
        """

        self._portfolio = None

    # =====================================================
    # Refresh
    # =====================================================

    def refresh(self):
        """
        Clear the cache and immediately rebuild the portfolio.
        """

        self.invalidate()

        return self.get_portfolio()


# =========================================================
# Singleton Cache
# =========================================================

portfolio_cache = PortfolioCache()