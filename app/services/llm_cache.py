"""
LLM Response Cache

Simple in-memory cache to avoid redundant API calls for the same queries.
Can be extended to use Redis or other persistent cache backends.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class LLMCache:
    """
    Simple in-memory cache for LLM responses.

    Cache keys are based on query hash + location hash.
    Cache entries expire after a configurable TTL.
    """

    def __init__(self, ttl_hours: int = 24):
        """
        Initialize cache.

        Args:
            ttl_hours: Time-to-live for cache entries in hours (default: 24)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_hours = ttl_hours
        logger.info(f"LLM cache initialized with TTL: {ttl_hours} hours")

    def _make_key(self, query: str, location: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key from query and location."""
        key_data = {"query": query, "location": location or {}}
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(
        self, query: str, location: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response if available and not expired.

        Args:
            query: Search query
            location: Optional location filter

        Returns:
            Cached response dict or None if not found/expired
        """
        key = self._make_key(query, location)
        entry = self.cache.get(key)

        if entry is None:
            return None

        # Check if expired
        cached_at = datetime.fromisoformat(entry["cached_at"])
        if datetime.now() - cached_at > timedelta(hours=self.ttl_hours):
            logger.debug(f"Cache entry expired for query: {query[:50]}...")
            del self.cache[key]
            return None

        logger.debug(f"Cache hit for query: {query[:50]}...")
        return entry["response"]

    def set(
        self,
        query: str,
        response: Dict[str, Any],
        location: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Cache a response.

        Args:
            query: Search query
            response: Response dict to cache
            location: Optional location filter
        """
        key = self._make_key(query, location)
        self.cache[key] = {
            "response": response,
            "cached_at": datetime.now().isoformat(),
        }
        logger.debug(f"Cached response for query: {query[:50]}...")

    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cleared {count} cache entries")

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self.cache),
            "ttl_hours": self.ttl_hours,
        }


# Global cache instance
_global_cache: Optional[LLMCache] = None


def get_cache(ttl_hours: int = 24) -> LLMCache:
    """Get or create global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = LLMCache(ttl_hours=ttl_hours)
    return _global_cache
