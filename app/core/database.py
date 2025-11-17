"""
Database configuration for Rajniti application.

Simple PostgreSQL setup without any schema definitions yet.
"""
import logging
import os

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# SQLAlchemy base for future models
Base = declarative_base()

# Global engine and session factory (used for simple setup)
# Note: In production, consider using Flask-SQLAlchemy or similar
# for better integration with Flask's application context
engine = None
SessionLocal = None


def init_db(app=None):
    """
    Initialize database connection.

    Args:
        app: Flask application instance (optional)
    """
    global engine, SessionLocal

    # Get database URL from environment or config
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        logger.warning("DATABASE_URL not set. Database will not be initialized.")
        return False

    try:
        # Create engine
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verify connections before using
            echo=False,  # Set to True for SQL query logging
        )

        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info("Database connection established successfully")
        return True

    except SQLAlchemyError as e:
        logger.error(f"Database error during initialization: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error initializing database: {str(e)}")
        return False


def get_db():
    """
    Get a database session.

    Yields:
        Session: SQLAlchemy database session
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_health():
    """
    Check if database connection is healthy.

    Returns:
        bool: True if database is healthy, False otherwise
    """
    if engine is None:
        return False

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during health check: {str(e)}")
        return False
