"""
Database models package.

Only User model is stored in the database.
Election data (candidates, parties, constituencies) is served from JSON files.
"""

from .user import User

__all__ = ["User"]
