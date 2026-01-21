"""
Base database model and utilities.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Automatically commits on success and rolls back on error.

    Usage:
        with get_db_session() as session:
            # Use session
            session.add(obj)
    """
    from .session import SessionLocal, init_engine

    if SessionLocal is None:
        init_engine()

    if SessionLocal is None:
        raise RuntimeError(
            "Database session factory not initialized. "
            "Set DATABASE_URL or avoid DB-backed features."
        )

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
