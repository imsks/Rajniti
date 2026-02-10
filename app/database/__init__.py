"""
Database package for Rajniti Election Data API.

Only the User table is stored in the database.
All election data (candidates, parties, constituencies) is served from JSON files.
"""

from .base import Base, get_db_session
from .config import get_database_url
from .session import SessionLocal, engine, init_db, init_engine

__all__ = [
    "Base",
    "SessionLocal",
    "engine",
    "init_db",
    "init_engine",
    "get_db_session",
    "get_database_url",
]
