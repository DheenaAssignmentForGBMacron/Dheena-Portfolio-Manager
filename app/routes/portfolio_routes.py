from flask import Blueprint, render_template

from app.services.snapshot_service import save_snapshot
from app.services.analytics_service import get_portfolio_analytics
from app.services.asset_analytics_service import get_asset_analytics
from app.services.portfolio_service import get_holding
from app.services.transaction_service import get_asset_transactions


portfolio_bp = Blueprint("portfolio", __name__)


# ---------------------------------
# Portfolio
# ---------------------------------

@portfolio_bp.route("/portfolio")
def portfolio():

    save_snapshot()

    analytics = get_portfolio_analytics()

    return render_template(
        "portfolio.html",
        assets=analytics["holdings"],
        allocation=analytics["allocation"],
        summary=analytics["summary"],
        performance=analytics["performance"],
        asset_classes=analytics["asset_class_distribution"],
        top_gainers=analytics["top_gainers"],
        top_losers=analytics["top_losers"],
        monthly_investments=analytics["monthly_investments"],
        cashflow=analytics["cashflow"],
        portfolio_growth=analytics["portfolio_growth"],
    )


# ---------------------------------
# Asset Details
# ---------------------------------

@portfolio_bp.route("/portfolio/<int:asset_id>")
def asset_details(asset_id):

    holding = get_holding(asset_id)

    if holding is None:
        return "Asset not found", 404

    analytics = get_asset_analytics(asset_id)

    transactions = get_asset_transactions(asset_id)

    return render_template(
        "asset_details.html",
        holding=holding.to_dict(),
        analytics=analytics,
        transactions=transactions,
    )
