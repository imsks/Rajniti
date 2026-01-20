"""
Data Services Layer

This layer abstracts data access using JSON files as the primary data source.
All business logic for data retrieval and manipulation goes here.
"""

from .data_service import DataService
from .json_data_service import JsonDataService
from .llm_service import get_llm_service
from .candidate_agent import CandidateAgent
from app.config.llm_config import LLMProvider

# Create singleton instance - using JSON file service
data_service: DataService = JsonDataService()

__all__ = [
    "data_service",
    "DataService",
    "JsonDataService",
    "get_llm_service",
    "LLMProvider",
    "CandidateAgent",
]
