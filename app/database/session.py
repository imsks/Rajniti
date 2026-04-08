"""
Database session management.

Single source of truth for SQLAlchemy engine and session factory.
Works with: venv+local, venv+supabase, docker+local, docker+supabase.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import (
    get_connect_args,
    get_database_url,
    get_echo_mode,
    is_transaction_pooler,
)

logger = logging.getLogger(__name__)

engine = None
SessionLocal = None


def init_engine():
    """
    Lazily create the SQLAlchemy engine + session factory.

    Safe to call multiple times; only initializes once.
    Returns None (without error) when DATABASE_URL is not set.
    """
    global engine, SessionLocal

    if engine is not None and SessionLocal is not None:
        return engine

    try:
        database_url = get_database_url()
    except ValueError:
        return None

    if not database_url:
        return None

    try:
        engine = create_engine(
            database_url,
            echo=get_echo_mode(),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args=get_connect_args(),
        )
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
    except Exception:
        logger.exception("Failed to create SQLAlchemy engine")
        engine = None
        SessionLocal = None
        return None

    return engine


def init_db():
    """Create all tables defined in ORM models."""
    from .base import Base
    from .models import User  # noqa: F401

    db_engine = init_engine()
    if db_engine is None:
        raise RuntimeError(
            "Database is not configured. Set DATABASE_URL to initialize tables."
        )

    url = get_database_url()
    if is_transaction_pooler(url):
        logger.warning(
            "DATABASE_URL looks like a transaction pooler (:6543 / pooler host). "
            "DDL may fail — use Supabase direct URL (port 5432) instead."
        )

    with db_engine.begin() as conn:
        Base.metadata.create_all(bind=conn)
