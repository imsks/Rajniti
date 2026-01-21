"""
Data Services Layer

This layer abstracts data access using JSON files as the primary data source.
All business logic for data retrieval and manipulation goes here.
"""

import os

from .data_service import DataService
from .db_data_service import DbDataService
from .json_data_service import JsonDataService
from .llm_service import get_llm_service
from .candidate_agent import CandidateAgent
from app.config.llm_config import LLMProvider

def _select_data_service() -> DataService:
    """
    Select the data backend.

    - DATA_BACKEND=json (default): read from `app/data/**` JSON datasets
    - DATA_BACKEND=db: use SQLAlchemy/Postgres
    """
    backend = os.getenv("DATA_BACKEND", "json").strip().lower()
    if backend == "db":
        return DbDataService()
    return JsonDataService()


# Create singleton instance
data_service: DataService = _select_data_service()

__all__ = [
    "data_service",
    "DataService",
    "DbDataService",
    "JsonDataService",
    "get_llm_service",
    "LLMProvider",
    "CandidateAgent",
]
