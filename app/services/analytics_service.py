from collections import OrderedDict
from datetime import datetime

from app.services.portfolio_service import get_portfolio
from app.services.transaction_service import get_transactions
from app.services.snapshot_service import get_snapshots


# =====================================================
# Portfolio Analytics
# =====================================================

def get_portfolio_analytics():

    portfolio = get_portfolio()

    holdings = portfolio["holdings"]
    summary = portfolio["summary"]

    return {
        "summary": summary,
        "holdings": holdings,

        "allocation": _build_allocation(
            holdings
        ),

        "asset_class_distribution": (
            _build_asset_class_distribution(
                holdings
            )
        ),

        "top_gainers": _build_top_gainers(
            holdings
        ),

        "top_losers": _build_top_losers(
            holdings
        ),

        "portfolio_insights": (
            _build_portfolio_insights(
                holdings
            )
        ),

        "performance": _build_performance(
            summary
        ),

        "monthly_investments": (
            _build_monthly_investments()
        ),

        "cashflow": _build_cashflow(),

        "portfolio_growth": (
            _build_portfolio_growth()
        ),
    }


# =====================================================
# Allocation
# =====================================================

def _build_allocation(holdings):

    allocation = [
        {
            "symbol": holding["symbol"],
            "name": holding["name"],
            "value": holding["current"],
            "allocation": holding["allocation"],
        }
        for holding in holdings
        if holding["current"] > 0
    ]

    return sorted(
        allocation,
        key=lambda item: item["value"],
        reverse=True,
    )


# =====================================================
# Asset Class Distribution
# =====================================================

def _build_asset_class_distribution(holdings):

    distribution = {}

    for holding in holdings:

        asset_type = holding["type"]

        distribution.setdefault(
            asset_type,
            0,
        )

        distribution[asset_type] += (
            holding["current"]
        )

    return distribution


# =====================================================
# Top Gainers
# =====================================================

def _build_top_gainers(holdings):

    return sorted(
        [
            holding
            for holding in holdings
            if holding["unrealized_pl"] > 0
        ],
        key=lambda item: item["unrealized_pl"],
        reverse=True,
    )[:5]


# =====================================================
# Top Losers
# =====================================================

def _build_top_losers(holdings):

    return sorted(
        [
            holding
            for holding in holdings
            if holding["unrealized_pl"] < 0
        ],
        key=lambda item: item["unrealized_pl"],
    )[:5]


# =====================================================
# Portfolio Insights
# =====================================================

def _build_portfolio_insights(holdings):

    if not holdings:

        return {
            "largest_holding": None,
            "best_performer": None,
            "worst_performer": None,
            "highest_allocation": None,
            "total_holdings": 0,
            "stock_count": 0,
            "etf_count": 0,
            "mutual_fund_count": 0,
        }

    active_holdings = [
        holding
        for holding in holdings
        if holding["qty"] > 0
    ]

    return {
        "largest_holding": (
            max(
                active_holdings,
                key=lambda item: item["current"],
            )
            if active_holdings
            else None
        ),

        "best_performer": max(
            holdings,
            key=lambda item: item["unrealized_pl"],
        ),

        "worst_performer": min(
            holdings,
            key=lambda item: item["unrealized_pl"],
        ),

        "highest_allocation": (
            max(
                active_holdings,
                key=lambda item: item["allocation"],
            )
            if active_holdings
            else None
        ),

        "total_holdings": len(
            active_holdings
        ),

        "stock_count": sum(
            1
            for holding in active_holdings
            if holding["type"] == "Stock"
        ),

        "etf_count": sum(
            1
            for holding in active_holdings
            if holding["type"] == "ETF"
        ),

        "mutual_fund_count": sum(
            1
            for holding in active_holdings
            if holding["type"] == "Mutual Fund"
        ),
    }


# =====================================================
# Performance
# =====================================================

def _build_performance(summary):

    return {
        "invested": summary["invested"],
        "current": summary["current"],

        "realized_pl": summary["realized_pl"],
        "unrealized_pl": summary["unrealized_pl"],
        "total_pl": summary["total_pl"],

        "return_pct": summary["return_pct"],

        "brokerage": summary["brokerage"],
        "dividend": summary["dividend"],
        "bonus": summary["bonus"],
    }


# =====================================================
# Monthly Investments
# =====================================================

def _build_monthly_investments():

    transactions = get_transactions()

    monthly = OrderedDict()

    for transaction in sorted(
        transactions,
        key=lambda item: item["transaction_date"],
    ):

        if transaction["transaction_type"] != "BUY":
            continue

        month = datetime.strptime(
            transaction["transaction_date"],
            "%Y-%m-%d",
        ).strftime("%b %Y")

        amount = (
            transaction["quantity"]
            * transaction["price"]
        ) + (
            transaction["brokerage"] or 0
        )

        monthly.setdefault(
            month,
            0,
        )

        monthly[month] += amount

    return [
        {
            "month": month,
            "amount": round(
                value,
                2,
            ),
        }
        for month, value in monthly.items()
    ]


# =====================================================
# Cash Flow
# =====================================================

def _build_cashflow():

    transactions = get_transactions()

    monthly = OrderedDict()

    for transaction in sorted(
        transactions,
        key=lambda item: item["transaction_date"],
    ):

        month = datetime.strptime(
            transaction["transaction_date"],
            "%Y-%m-%d",
        ).strftime("%b %Y")

        monthly.setdefault(
            month,
            {
                "buy": 0,
                "sell": 0,
                "dividend": 0,
            },
        )

        quantity = (
            transaction["quantity"] or 0
        )

        price = (
            transaction["price"] or 0
        )

        brokerage = (
            transaction["brokerage"] or 0
        )

        amount = quantity * price

        transaction_type = (
            transaction["transaction_type"]
        )

        if transaction_type == "BUY":

            monthly[month]["buy"] += (
                amount + brokerage
            )

        elif transaction_type == "SELL":

            # Sale proceeds are reduced by brokerage.
            monthly[month]["sell"] += (
                amount - brokerage
            )

        elif transaction_type == "DIVIDEND":

            monthly[month]["dividend"] += (
                amount
            )

    return [
        {
            "month": month,

            "buy": round(
                values["buy"],
                2,
            ),

            "sell": round(
                values["sell"],
                2,
            ),

            "dividend": round(
                values["dividend"],
                2,
            ),

            "net": round(
                values["sell"]
                + values["dividend"]
                - values["buy"],
                2,
            ),
        }

        for month, values in monthly.items()
    ]


# =====================================================
# Portfolio Growth
# =====================================================

def _build_portfolio_growth():

    """
    Build historical portfolio value from daily snapshots.

    IMPORTANT:
    This is intentionally based on portfolio_snapshots
    rather than transactions.

    Transactions tell us how much money was invested.
    Snapshots tell us what the portfolio was actually
    worth at a point in time.
    """

    snapshots = get_snapshots()

    growth = []

    for snapshot in snapshots:

        snapshot_date = snapshot["snapshot_date"]

        current_value = (
            snapshot["current_value"]
        )

        growth.append(
            {
                # Keep "month" for backward compatibility
                # with existing frontend code.
                "month": snapshot_date,

                # Proper historical date.
                "date": snapshot_date,

                # Actual portfolio market value.
                "value": round(
                    current_value,
                    2,
                ),

                # Additional historical information
                # available to future charts.
                "invested": round(
                    snapshot["invested"],
                    2,
                ),

                "profit": round(
                    snapshot["profit"],
                    2,
                ),

                "return_pct": round(
                    snapshot["return_pct"],
                    2,
                ),
            }
        )

    return growth