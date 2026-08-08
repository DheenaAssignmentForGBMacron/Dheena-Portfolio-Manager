from collections import OrderedDict
from datetime import datetime

from app.services.portfolio_service import get_portfolio
from app.services.transaction_service import get_transactions


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
        "allocation": _build_allocation(holdings),
        "asset_class_distribution": _build_asset_class_distribution(
            holdings
        ),
        "top_gainers": _build_top_gainers(holdings),
        "top_losers": _build_top_losers(holdings),
        "portfolio_insights": _build_portfolio_insights(holdings),
        "performance": _build_performance(summary),
        "monthly_investments": _build_monthly_investments(),
        "cashflow": _build_cashflow(),
        "portfolio_growth": _build_portfolio_growth(),
    }


# =====================================================
# Allocation
# =====================================================

def _build_allocation(holdings):

    allocation = [
        {
            "symbol": h["symbol"],
            "name": h["name"],
            "value": h["current"],
            "allocation": h["allocation"],
        }
        for h in holdings
    ]

    return sorted(
        allocation,
        key=lambda x: x["value"],
        reverse=True,
    )


# =====================================================
# Asset Class Distribution
# =====================================================

def _build_asset_class_distribution(holdings):

    distribution = {}

    for holding in holdings:

        distribution.setdefault(
            holding["type"],
            0,
        )

        distribution[holding["type"]] += holding["current"]

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
        key=lambda x: x["unrealized_pl"],
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
        key=lambda x: x["unrealized_pl"],
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

    return {
        "largest_holding": max(
            holdings,
            key=lambda x: x["current"],
        ),
        "best_performer": max(
            holdings,
            key=lambda x: x["unrealized_pl"],
        ),
        "worst_performer": min(
            holdings,
            key=lambda x: x["unrealized_pl"],
        ),
        "highest_allocation": max(
            holdings,
            key=lambda x: x["allocation"],
        ),
        "total_holdings": len(holdings),
        "stock_count": sum(
            1 for h in holdings
            if h["type"] == "Stock"
        ),
        "etf_count": sum(
            1 for h in holdings
            if h["type"] == "ETF"
        ),
        "mutual_fund_count": sum(
            1 for h in holdings
            if h["type"] == "Mutual Fund"
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

    for tx in sorted(
        transactions,
        key=lambda x: x["transaction_date"],
    ):

        if tx["transaction_type"] != "BUY":
            continue

        month = datetime.strptime(
            tx["transaction_date"],
            "%Y-%m-%d",
        ).strftime("%b %Y")

        amount = (
            tx["quantity"] * tx["price"]
        ) + tx["brokerage"]

        monthly.setdefault(month, 0)
        monthly[month] += amount

    return [
        {
            "month": month,
            "amount": round(value, 2),
        }
        for month, value in monthly.items()
    ]


# =====================================================
# Cash Flow
# =====================================================

def _build_cashflow():

    transactions = get_transactions()

    monthly = OrderedDict()

    for tx in sorted(
        transactions,
        key=lambda x: x["transaction_date"],
    ):

        month = datetime.strptime(
            tx["transaction_date"],
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

        amount = (
            tx["quantity"] * tx["price"]
        ) + tx["brokerage"]

        if tx["transaction_type"] == "BUY":

            monthly[month]["buy"] += amount

        elif tx["transaction_type"] == "SELL":

            monthly[month]["sell"] += amount

        elif tx["transaction_type"] == "DIVIDEND":

            monthly[month]["dividend"] += amount

    return [
        {
            "month": month,
            "buy": round(values["buy"], 2),
            "sell": round(values["sell"], 2),
            "dividend": round(values["dividend"], 2),
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

    transactions = get_transactions()

    monthly = OrderedDict()

    cumulative = 0

    for tx in sorted(
        transactions,
        key=lambda x: x["transaction_date"],
    ):

        if tx["transaction_type"] != "BUY":
            continue

        month = datetime.strptime(
            tx["transaction_date"],
            "%Y-%m-%d",
        ).strftime("%b %Y")

        amount = (
            tx["quantity"] * tx["price"]
        ) + tx["brokerage"]

        monthly.setdefault(month, 0)
        monthly[month] += amount

    growth = []

    for month, value in monthly.items():

        cumulative += value

        growth.append(
            {
                "month": month,
                "value": round(cumulative, 2),
            }
        )

    return growth