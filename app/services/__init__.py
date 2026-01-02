"""
Data Services Layer

This layer abstracts data access so we can easily switch from JSON to database later.
All business logic for data retrieval and manipulation goes here.
"""

from .data_service import DataService
from .db_data_service import DbDataService
from .llm_service import get_llm_service
from .candidate_agent import CandidateAgent
from app.config.llm_config import LLMProvider

# Create singleton instance - using database service
data_service: DataService = DbDataService()

__all__ = [
    "data_service",
    "DataService",
    "DbDataService",
    "get_llm_service",
    "LLMProvider",
    "CandidateAgent",
]
