"""
Data Models for Rajniti Election API

Simple Pydantic models that match our existing JSON data structure.
These models can be used with JSON storage now and easily adapted for DB later.
"""

from .candidate import Candidate
from .constituency import Constituency
from .election import Election, ElectionType
from .party import Party

__all__ = [
    "Candidate",
    "Party",
    "Constituency",
    "Election",
    "ElectionType",
]
