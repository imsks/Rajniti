"""
Database session management.

Creates SQLAlchemy engine and session factory.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import get_database_url, get_echo_mode

# Create database engine
# Works with both local PostgreSQL and Supabase (PostgreSQL-based)
engine = create_engine(
    get_database_url(),
    echo=get_echo_mode(),
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def init_db():
    """
    Initialize database tables.

    Creates all tables defined in models.
    """
    from .base import Base

    # Import all models to register them
    from .models import Candidate, Constituency, Election, Party  # noqa: F401

    Base.metadata.create_all(bind=engine)
