"""
Database models package.

Includes Party, Constituency, Candidate, and Election models with CRUD operations.
"""

from .candidate import Candidate
from .constituency import Constituency
from .election import Election
from .party import Party

__all__ = ["Party", "Constituency", "Candidate", "Election"]
