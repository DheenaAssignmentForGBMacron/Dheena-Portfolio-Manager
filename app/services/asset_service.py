"""
Asset Service

Application-level operations for assets.

Asset persistence is handled by AssetRepository.

Portfolio position calculations are handled by PortfolioService
and PortfolioEngine. This service only combines those results
when the presentation layer needs asset metadata together with
current holdings.
"""

from app.repositories.asset_repository import AssetRepository
from app.services.portfolio_service import get_holdings


_repository = AssetRepository()


# =====================================================
# Create
# =====================================================

def add_asset(
    symbol,
    name,
    asset_class,
    exchange,
):
    """Create a new asset."""

    return _repository.add(
        symbol,
        name,
        asset_class,
        exchange,
    )


# =====================================================
# Read
# =====================================================

def get_assets():
    """Return all registered assets."""

    return _repository.get_all()


def get_asset(asset_id):
    """Return one asset by ID."""

    return _repository.get(asset_id)


def search_assets(search_text):
    """Search assets by symbol or name."""

    return _repository.search(search_text)


# =====================================================
# Assets + Current Holdings
# =====================================================

def get_assets_with_holdings():
    """
    Return asset metadata together with current holdings.

    AssetRepository owns asset persistence.
    PortfolioService owns transaction-derived positions.

    This function composes the two for presentation purposes.
    """

    assets = get_assets()
    holdings = get_holdings()

    result = []

    for asset in assets:

        holding = holdings.get(asset["id"])

        result.append(
            {
                "id": asset["id"],
                "symbol": asset["symbol"],
                "name": asset["name"],
                "asset_class": asset["asset_class"],
                "exchange": asset["exchange"],
                "holdings": (
                    holding.qty
                    if holding is not None
                    else 0.0
                ),
            }
        )

    return result


# =====================================================
# Summary
# =====================================================

def get_asset_summary():
    """Return aggregate asset counts."""

    return _repository.get_summary()