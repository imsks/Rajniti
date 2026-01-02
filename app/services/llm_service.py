"""
LLM Service using Langchain

This module provides a unified LLM service using Langchain abstractions.
It supports multiple providers (OpenAI, Perplexity) through a single interface.
"""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config.llm_config import LLMProvider, get_llm_config

logger = logging.getLogger(__name__)


class LLMService:
    """
    Unified LLM service using Langchain.

    This service provides a clean, provider-agnostic interface for LLM operations.
    It uses Langchain's chat model abstractions to support multiple providers.
    """

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize the LLM service.

        Args:
            provider: Provider name ('openai', 'perplexity').
                     If None, uses the default provider from config.
        """
        self.config = get_llm_config()

        # Determine which provider to use
        if provider:
            try:
                self.provider = LLMProvider(provider.lower())
            except ValueError:
                logger.warning(
                    f"Invalid provider '{provider}', using default: {self.config.default_provider}"
                )
                self.provider = self.config.default_provider
        else:
            self.provider = self.config.default_provider

        # Get provider configuration
        self.provider_config = self.config.get_provider_config(self.provider)

        # Initialize the appropriate Langchain chat model
        self.chat_model = self._create_chat_model()

        logger.info(f"LLM Service initialized with provider: {self.provider}")

    def _create_chat_model(self):
        """
        Create the appropriate Langchain chat model based on provider.

        Returns:
            Langchain chat model instance
        """
        if self.provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                api_key=self.provider_config.api_key,
                model=self.provider_config.model,
                temperature=self.provider_config.temperature,
                max_tokens=self.provider_config.max_tokens,
            )
        elif self.provider == LLMProvider.PERPLEXITY:
            # Perplexity uses OpenAI-compatible API
            return ChatOpenAI(
                api_key=self.provider_config.api_key,
                model=self.provider_config.model,
                temperature=self.provider_config.temperature,
                max_tokens=self.provider_config.max_tokens,
                base_url="https://api.perplexity.ai",
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def search(
        self,
        query: str,
        location: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Search using LLM with optional location filter.

        Args:
            query: Search query string
            location: Optional location dict with keys like 'country', 'region', 'city'

        Returns:
            Dict containing 'query', 'answer', 'citations', 'model', and 'location'
        """
        # Build system message with context
        system_content = (
            "You are a helpful assistant that provides accurate information "
            "about Indian politics and elections. Focus on facts and cite sources when possible."
        )

        # Enhance query with location context if provided
        enhanced_query = query
        if location:
            location_parts = []
            if location.get("country"):
                location_parts.append(location["country"])
            if location.get("region"):
                location_parts.append(location["region"])
            if location.get("city"):
                location_parts.append(location["city"])

            if location_parts:
                location_str = ", ".join(location_parts)
                enhanced_query = f"{query} (Context: {location_str})"

        try:
            # Create messages
            messages = [
                SystemMessage(content=system_content),
                HumanMessage(content=enhanced_query),
            ]

            # Invoke the chat model
            response = self.chat_model.invoke(messages)

            return {
                "query": query,
                "answer": response.content,
                "citations": [],  # Langchain doesn't provide citations by default
                "model": self.provider_config.model,
                "location": location or {},
            }

        except Exception as e:
            logger.error(f"LLM search error: {e}")
            return {
                "query": query,
                "error": str(e),
                "answer": None,
                "citations": [],
            }

    def search_india(
        self,
        query: str,
        region: Optional[str] = None,
        city: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Convenience method for India-specific searches.

        Args:
            query: Search query string
            region: Indian state/region
            city: Indian city

        Returns:
            Dict containing search results
        """
        location = {"country": "IN"}

        if region:
            location["region"] = region

        if city:
            location["city"] = city

        return self.search(query, location=location)

    def batch_search(
        self,
        queries: List[str],
        location: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search multiple queries.

        Args:
            queries: List of search query strings
            location: Optional location filter

        Returns:
            List of result dicts, one per query
        """
        if len(queries) == 1:
            return [self.search(queries[0], location=location)]

        # For batch queries, we can combine them into a single request
        # to optimize API usage
        combined_query = (
            "I need information about the following topics. "
            "Please provide answers in a structured format:\n\n"
        )
        for i, query in enumerate(queries, 1):
            combined_query += f"{i}. {query}\n"

        combined_query += (
            "\nPlease provide detailed answers for each topic, "
            "separated clearly. Focus on factual information."
        )

        try:
            result = self.search(combined_query, location=location)
            if result.get("error"):
                # Fallback to individual queries on error
                return [self.search(q, location=location) for q in queries]

            # For simplicity, return the combined result for all queries
            # In production, you might parse the response to separate answers
            # Create individual result objects for each query with correct query field
            results = []
            for query in queries:
                query_result = result.copy()
                query_result["query"] = query
                results.append(query_result)
            return results

        except Exception as e:
            logger.error(f"Batch search error: {e}")
            # Fallback to individual queries
            return [self.search(q, location=location) for q in queries]


def get_llm_service(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
) -> LLMService:
    """
    Factory function to get the LLM service.

    Args:
        provider: Provider name ('openai', 'perplexity').
                 If None, uses the default provider from config.
        api_key: Optional API key (deprecated - use environment variables instead).

    Returns:
        LLMService instance

    Example:
        >>> service = get_llm_service('openai')
        >>> results = service.search("election results")
    """
    if api_key:
        logger.warning(
            "Passing api_key directly is deprecated. "
            "Use environment variables instead (e.g., OPENAI_API_KEY)."
        )

    return LLMService(provider=provider)
