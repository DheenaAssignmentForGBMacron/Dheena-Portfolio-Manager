from app.repositories.portfolio_repository import repository


# =====================================================
# Portfolio
# =====================================================

def get_portfolio():
    """
    Returns the current portfolio.

    Uses the repository cache until the portfolio
    is explicitly invalidated.
    """

    result = repository.get_portfolio()

    return {
        "holdings": [
            holding.to_dict()
            for holding in result["holdings"].values()
        ],
        "summary": result["summary"],
    }


# =====================================================
# Single Holding
# =====================================================

def get_holding(asset_id):
    """
    Returns a single holding.
    """

    result = repository.get_portfolio()

    return result["holdings"].get(asset_id)


# =====================================================
# Raw Holdings
# =====================================================

def get_holdings():
    """
    Returns raw Holding objects.
    """

    return repository.get_portfolio()["holdings"]


# =====================================================
# Invalidate Portfolio Cache
# =====================================================

def invalidate_portfolio():
    """
    Clears the cached portfolio.

    The next portfolio request will rebuild the
    portfolio from the database.
    """

    repository.invalidate()


# =====================================================
# Refresh Portfolio
# =====================================================

def refresh_portfolio():
    """
    Clears the portfolio cache and immediately rebuilds it.
    """

    repository.invalidate()

    return repository.get_portfolio()