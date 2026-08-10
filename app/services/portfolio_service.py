"""
Portfolio Service

Application-facing interface for portfolio data.

PortfolioService does not perform portfolio calculations
itself. It delegates calculation and caching to PortfolioCache.

This layer converts domain Holding objects into dictionaries
for API/template consumers where appropriate.
"""

from app.services.portfolio_cache import portfolio_cache


# =========================================================
# Portfolio
# =========================================================

def get_portfolio():
    """
    Return the current portfolio in presentation-friendly form.

    The underlying portfolio is obtained from PortfolioCache.
    """

    result = portfolio_cache.get_portfolio()

    return {
        "holdings": [
            holding.to_dict()
            for holding in result["holdings"].values()
        ],
        "summary": result["summary"],
    }


# =========================================================
# Single Holding
# =========================================================

def get_holding(asset_id):
    """
    Return a single raw Holding object by asset ID.

    Returns None when the asset does not exist.
    """

    result = portfolio_cache.get_portfolio()

    return result["holdings"].get(asset_id)


# =========================================================
# Raw Holdings
# =========================================================

def get_holdings():
    """
    Return the raw Holding objects keyed by asset ID.
    """

    return portfolio_cache.get_portfolio()["holdings"]


# =========================================================
# Invalidate Portfolio
# =========================================================

def invalidate_portfolio() -> None:
    """
    Invalidate the cached portfolio.

    The next portfolio request will rebuild the portfolio.
    """

    portfolio_cache.invalidate()


# =========================================================
# Refresh Portfolio
# =========================================================

def refresh_portfolio():
    """
    Invalidate the cache and immediately rebuild the portfolio.
    """

    return portfolio_cache.refresh()