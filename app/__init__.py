"""
Dheena Portfolio Manager application factory.
"""

from flask import Flask

from app.config import Config
from app.filters import currency, format_date


def create_app(config_class=Config) -> Flask:
    """
    Create and configure the DPM Flask application.

    Route modules never create or import the Flask application directly.
    """

    app = Flask(__name__)

    app.config.from_object(config_class)

    # Jinja filters
    app.jinja_env.filters["currency"] = currency
    app.jinja_env.filters["format_date"] = format_date

    # -------------------------------------------------
    # Blueprint registration
    # -------------------------------------------------

    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.portfolio_routes import portfolio_bp
    from app.routes.asset_routes import assets_bp
    from app.routes.transaction_routes import transaction_bp
    from app.routes.analytics_routes import analytics_bp
    from app.routes.api_routes import api_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(api_bp)

    # Debug routes are development-only.
    if app.config["DEBUG"]:

        from app.routes.debug_routes import debug_bp

        app.register_blueprint(debug_bp)

    return app