"""LLM Service stub (Langchain removed)

This file provides a minimal LLMService shim so other parts of the
application that import this module do not break. The real LLM agent
will be implemented from scratch (using a fresh LangChain/Langraph
integration) in a follow-up task.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class LLMService:
    """
    Placeholder LLM service. Methods return a clear not-implemented
    response so callers can detect and the implementation can be
    replaced incrementally.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or "none"
        logger.info("LLMService initialized as stub (Langchain removed)")

    def search(self, query: str, location: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "query": query,
            "answer": None,
            "error": "LLMService not implemented. Langchain integration removed.",
            "citations": [],
            "model": None,
            "location": location or {},
        }

    def search_india(self, query: str, region: Optional[str] = None, city: Optional[str] = None) -> Dict[str, Any]:
        location = {"country": "IN"}
        if region:
            location["region"] = region
        if city:
            location["city"] = city
        return self.search(query, location=location)

    def batch_search(self, queries: List[str], location: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        results = []
        for q in queries:
            results.append(self.search(q, location=location))
        return results


def get_llm_service(provider: Optional[str] = None, api_key: Optional[str] = None) -> LLMService:
    if api_key:
        logger.warning("Passing api_key directly is deprecated. Use environment variables instead.")
    return LLMService(provider=provider)

