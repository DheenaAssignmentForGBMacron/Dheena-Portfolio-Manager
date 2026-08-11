"""
DPM development entry point.

Production deployments should use the Flask application factory
directly rather than relying on this module.
"""

from app import create_app
from app.database import initialize_database
from app.services.asset_service import seed_assets


def bootstrap() -> None:
    """
    Prepare the database and required master data.
    """

    initialize_database()
    seed_assets()


app = create_app()


if __name__ == "__main__":

    bootstrap()

    app.run(
        debug=app.config["DEBUG"],
    )