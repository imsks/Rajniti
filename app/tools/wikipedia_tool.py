"""
Wikipedia lookup tool — uses the free MediaWiki REST API (no key needed).

Great for Indian-politician biographical context: education, elections,
party history, family — all from a single ``politician_context()`` call.
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_API = "https://en.wikipedia.org/w/api.php"
_REST = "https://en.wikipedia.org/api/rest_v1"
_HEADERS = {
    "User-Agent": "Rajniti/1.0 (https://github.com/rajniti; bot@rajniti.dev)",
    "Accept": "application/json",
}


class WikipediaTool:
    """Search and summarize Wikipedia articles."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def search(self, query: str, limit: int = 3) -> list[dict[str, str]]:
        """Return ``[{title, snippet}, ...]`` from Wikipedia search."""
        try:
            resp = httpx.get(
                _API,
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": limit,
                    "format": "json",
                },
                headers=_HEADERS,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            hits = resp.json().get("query", {}).get("search", [])
            return [
                {"title": h["title"], "snippet": h.get("snippet", "")} for h in hits
            ]
        except Exception as exc:
            logger.warning("Wikipedia search failed for %r: %s", query, exc)
            return []

    def summary(self, title: str) -> Optional[str]:
        """Fetch the plain-text extract of a Wikipedia article."""
        try:
            safe = title.replace(" ", "_")
            resp = httpx.get(
                f"{_REST}/page/summary/{safe}",
                headers=_HEADERS,
                timeout=self.timeout,
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json().get("extract")
        except Exception as exc:
            logger.warning("Wikipedia summary failed for %r: %s", title, exc)
            return None

    def search_and_summarize(self, query: str) -> Optional[str]:
        """Search Wikipedia and return the summary of the best match."""
        hits = self.search(query, limit=1)
        if not hits:
            return None
        return self.summary(hits[0]["title"])

    def politician_context(self, name: str, state: str = "", party: str = "") -> str:
        """Build a context block about an Indian politician from Wikipedia."""
        query = f"{name} Indian politician"
        if state:
            query += f" {state}"

        text = self.search_and_summarize(query)
        return f"Wikipedia: {text}" if text else ""
