from app import create_app
from app.database import get_connection
from app.services.asset_service import seed_assets


def initialize_database() -> None:
    """
    Initialize the database schema and seed master data.
    Safe to execute on every application startup.
    """
    conn = get_connection()

    with open("database/schema.sql", encoding="utf-8") as file:
        conn.executescript(file.read())

    conn.commit()
    conn.close()

    seed_assets()


if __name__ == "__main__":
    initialize_database()
    app = create_app()
    app.run(debug=True)
