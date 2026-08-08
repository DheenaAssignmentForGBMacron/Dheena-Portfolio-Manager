from flask import Flask
from app.filters import currency, format_date

def create_app() -> Flask:
    """
    Application factory for DPM.

    The factory creates exactly one Flask application instance per call and
    explicitly registers every route Blueprint. Route modules never import
    the Flask application directly.
    """
    app = Flask(__name__)
    app.secret_key = "dpm-secret-key"

    app.jinja_env.filters["currency"] = currency
    app.jinja_env.filters["format_date"] = format_date

    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.portfolio_routes import portfolio_bp
    from app.routes.asset_routes import assets_bp
    from app.routes.transaction_routes import transaction_bp
    from app.routes.analytics_routes import analytics_bp
    from app.routes.api_routes import api_bp
    from app.routes.debug_routes import debug_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(debug_bp)

    return app
