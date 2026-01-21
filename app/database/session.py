"""
Database session management.

Creates SQLAlchemy engine and session factory.
"""

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import get_database_url, get_echo_mode

# Lazily initialized to keep imports safe when DATABASE_URL / db driver is absent.
engine = None
SessionLocal = None


def init_db():
    """
    Initialize database tables.

    Creates all tables defined in models.
    """
    from .base import Base

    # Import all models to register them
    from .models import Candidate, Constituency, Election, Party  # noqa: F401

    eng = get_engine(required=True)
    Base.metadata.create_all(bind=eng)


def get_engine(required: bool = False):
    """
    Get or create the SQLAlchemy engine.

    Args:
        required: If True, raise if DATABASE_URL is missing.
    """
    global engine, SessionLocal
    if engine is not None and SessionLocal is not None:
        return engine

    database_url = get_database_url(required=required)
    if not database_url:
        if required:
            raise ValueError("DATABASE_URL is required to initialize the database engine.")
        return None

    engine = create_engine(
        database_url,
        echo=get_echo_mode(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine


def get_session_local(required: bool = False):
    """
    Get the configured sessionmaker, initializing lazily if needed.
    """
    global SessionLocal
    if SessionLocal is None:
        get_engine(required=required)
    return SessionLocal
