from flask import Blueprint, render_template

from app.services.analytics_service import (
    get_portfolio_analytics,
)

analytics_bp = Blueprint(
    "analytics",
    __name__,
)


@analytics_bp.route("/analytics")
def analytics():

    analytics = get_portfolio_analytics()

    return render_template(
        "analytics.html",
        summary=analytics["summary"],
        performance=analytics["performance"],
        asset_classes=analytics["asset_class_distribution"],
        top_gainers=analytics["top_gainers"],
        top_losers=analytics["top_losers"],
        monthly_investments=analytics["monthly_investments"],
        cashflow=analytics["cashflow"],
        portfolio_growth=analytics["portfolio_growth"],
    )