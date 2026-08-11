"""
Application configuration.

Keeps environment-specific configuration outside the Flask
application factory and business logic.
"""

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "dpm.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"


class Config:
    """Base application configuration."""

    SECRET_KEY = os.getenv(
        "DPM_SECRET_KEY",
        "dev-only-change-this-secret-key",
    )

    DATABASE_PATH = DATABASE_PATH
    SCHEMA_PATH = SCHEMA_PATH

    DEBUG = os.getenv(
        "DPM_DEBUG",
        "false",
    ).lower() == "true"

    TESTING = False


class TestingConfig(Config):
    """Configuration used by automated tests."""

    TESTING = True
    DEBUG = False

    SECRET_KEY = "dpm-test-secret-key"