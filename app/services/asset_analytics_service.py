from app.services.transaction_service import get_asset_transactions
from app.services.portfolio_service import get_holding


# =====================================================
# Asset Analytics
# =====================================================

def get_asset_analytics(asset_id):
    """
    Returns everything required by the
    Asset Details page.
    """

    holding = get_holding(asset_id)

    if holding is None:
        return None

    transactions = get_asset_transactions(asset_id)

    return {

        "position": _build_position_summary(holding),

        "performance": _build_performance_summary(holding),

        "transaction_summary": _build_transaction_summary(
            transactions
        ),

        "price_history": _build_price_history(
            transactions,
            holding.current_price
        ),

        "transactions": transactions,

    }


# =====================================================
# Position
# =====================================================

def _build_position_summary(holding):

    return {

        "asset_id": holding.asset_id,

        "symbol": holding.symbol,

        "name": holding.name,

        "asset_class": holding.asset_class,

        "quantity": holding.qty,

        "average_price": holding.avg,

        "market_price": holding.current_price,

        "invested": holding.invested,

        "current_value": holding.current_value,

        "allocation": holding.allocation,

    }


# =====================================================
# Performance
# =====================================================

def _build_performance_summary(holding):

    return {

        "unrealized_pl": holding.unrealized_pl,

        "realized_pl": holding.realized_pl,

        "total_pl": (
            holding.realized_pl +
            holding.unrealized_pl
        ),

        "brokerage": holding.brokerage,

        "dividend": holding.dividend,

        "bonus": holding.bonus,

        "return_pct": (
            round(
                (
                    holding.unrealized_pl /
                    holding.invested
                ) * 100,
                2
            )
            if holding.invested > 0
            else 0
        ),

    }


# =====================================================
# Transaction Summary
# =====================================================

def _build_transaction_summary(transactions):

    buy_count = 0
    sell_count = 0

    first_purchase = None
    last_transaction = None

    total_buy_qty = 0
    total_sell_qty = 0

    for tx in transactions:

        if tx["transaction_type"] == "BUY":

            buy_count += 1
            total_buy_qty += tx["quantity"]

            if first_purchase is None:
                first_purchase = tx["transaction_date"]

        elif tx["transaction_type"] == "SELL":

            sell_count += 1
            total_sell_qty += tx["quantity"]

        last_transaction = tx["transaction_date"]

    return {

        "buy_count": buy_count,

        "sell_count": sell_count,

        "total_transactions": len(transactions),

        "total_buy_qty": total_buy_qty,

        "total_sell_qty": total_sell_qty,

        "first_purchase": first_purchase,

        "last_transaction": last_transaction,

    }


# =====================================================
# Price History
# =====================================================

def _build_price_history(
    transactions,
    current_price
):
    """
    Temporary implementation.

    Later this will use Yahoo Finance.
    """

    history = []

    for tx in transactions:

        history.append({

            "date": tx["transaction_date"],

            "price": tx["price"]

        })

    if history:

        history.append({

            "date": history[-1]["date"],

            "price": current_price

        })

    return history