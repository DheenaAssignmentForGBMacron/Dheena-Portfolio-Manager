"""
DPM development entry point.

Production deployments should use the Flask application factory
directly rather than relying on this module.
"""

from app import create_app
from app.database import initialize_database


def bootstrap() -> None:
    """
    Prepare the database and required master data.
    """

    initialize_database()


app = create_app()


if __name__ == "__main__":

    bootstrap()

    app.run(
        debug=app.config["DEBUG"],
    )