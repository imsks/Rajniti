"""
Database session management.

Creates SQLAlchemy engine and session factory.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import get_database_url, get_echo_mode

engine = None
SessionLocal = None


def init_engine():
    """
    Lazily initialize the SQLAlchemy engine + session factory.

    IMPORTANT:
    - Do NOT create the engine at import time (keeps CLI/tools/tests usable without DB deps).
    - If DATABASE_URL is not set, the DB is considered "disabled".
    """
    global engine, SessionLocal

    if engine is not None and SessionLocal is not None:
        return engine

    try:
        database_url = get_database_url()
    except ValueError:
        # Database is optional for most workflows; only required for user persistence.
        return None

    engine = create_engine(
        database_url,
        echo=get_echo_mode(),
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,
        max_overflow=10,
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    return engine


def init_db():
    """
    Initialize database tables.

    Creates all tables defined in models.
    """
    from .base import Base

    # Ensure engine/session exist
    db_engine = init_engine()
    if db_engine is None:
        raise RuntimeError(
            "Database is not configured. Set DATABASE_URL to initialize tables."
        )

    # Import models to register them with SQLAlchemy metadata
    from .models import User  # noqa: F401

    Base.metadata.create_all(bind=db_engine)
