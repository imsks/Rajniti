"""
Database configuration for Rajniti application.

Delegates to the canonical app.database package for engine/session/Base
so there is a single source of truth for all DB operations.
"""

import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.config import get_database_url

logger = logging.getLogger(__name__)


def init_db(app=None):
    """
    Initialize database connection and create tables.

    Delegates to app.database.session which owns the engine, SessionLocal,
    and the Base that all models inherit from.

    Args:
        app: Flask application instance (optional, reserved for future use)
    """
    database_url = get_database_url(required=False)
    if not database_url:
        logger.warning("DATABASE_URL not set. Database will not be initialized.")
        return False

    try:
        from app.database.session import init_db as create_tables
        from app.database.session import init_engine

        db_engine = init_engine()
        if db_engine is None:
            logger.error("Failed to create database engine.")
            return False

        with db_engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        create_tables()

        logger.info("Database connection established and tables ensured")
        return True

    except SQLAlchemyError as e:
        logger.error(f"Database error during initialization: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error initializing database: {e}")
        return False


def check_db_health():
    """
    Check if database connection is healthy.

    Returns:
        bool: True if database is healthy, False otherwise
    """
    from app.database.session import engine

    if engine is None:
        return False

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database health check failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during health check: {e}")
        return False
