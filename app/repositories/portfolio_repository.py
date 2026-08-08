from app.services.portfolio_engine import PortfolioEngine


class PortfolioRepository:

    def __init__(self):
        self._portfolio = None

    # =====================================================
    # Get Portfolio
    # =====================================================

    def get_portfolio(self):

        if self._portfolio is None:
            self._portfolio = PortfolioEngine().process()

        return self._portfolio

    # =====================================================
    # Invalidate Cache
    # =====================================================

    def invalidate(self):
        """
        Clear the cached portfolio.

        The next call to get_portfolio() will rebuild
        the portfolio from the latest transactions and
        latest market prices.
        """

        self._portfolio = None


# =====================================================
# Singleton Repository
# =====================================================

repository = PortfolioRepository()
