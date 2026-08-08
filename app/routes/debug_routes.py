from flask import (
    Blueprint,
)

from app.services.portfolio_service import (
    get_portfolio,
)

from app.services.portfolio_engine import (
    PortfolioEngine,
)

debug_bp = Blueprint(
    "debug",
    __name__,
)


@debug_bp.route("/test")
def test():

    return {
        "data": get_portfolio()
    }


@debug_bp.route("/engine-test")
def engine_test():

    engine = PortfolioEngine()

    result = engine.process()

    return {
        "holdings": {
            holding_id: holding.to_dict()
            for holding_id, holding in result["holdings"].items()
        },
        "summary": result["summary"],
    }