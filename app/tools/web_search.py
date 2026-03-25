"""
Web-search tool — tries DuckDuckGo (``ddgs`` / ``duckduckgo-search``) first,
then falls back to a lightweight httpx-based DuckDuckGo HTML scrape.

Designed for graceful degradation: always returns a result (possibly empty),
never raises.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
# Strategy 1: ddgs / duckduckgo-search package
# ---------------------------------------------------------------------------


def _import_ddgs() -> Any:
    """Return the DDGS class from whichever package is available."""
    try:
        from ddgs import DDGS  # type: ignore[import-untyped]

        return DDGS
    except ImportError:
        pass
    try:
        from duckduckgo_search import DDGS  # type: ignore[import-untyped]

        return DDGS
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Strategy 2: lightweight httpx fallback (HTML-lite endpoint)
# ---------------------------------------------------------------------------


def _httpx_search(query: str, max_results: int, timeout: int) -> list[dict[str, str]]:
    """Scrape DuckDuckGo HTML-lite for search results (no JS required)."""
    try:
        resp = httpx.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": _UA},
            timeout=timeout,
            follow_redirects=True,
        )
        resp.raise_for_status()
    except Exception as exc:
        logger.debug("httpx fallback search failed: %s", exc)
        return []

    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(resp.text, "html.parser")
        results: list[dict[str, str]] = []
        for item in soup.select(".result"):
            title_tag = item.select_one(".result__a")
            snippet_tag = item.select_one(".result__snippet")
            if not title_tag:
                continue
            href = title_tag.get("href", "")
            if isinstance(href, list):
                href = href[0] if href else ""
            url_match = re.search(r"uddg=([^&]+)", href)
            url = ""
            if url_match:
                from urllib.parse import unquote

                url = unquote(url_match.group(1))
            results.append(
                {
                    "title": title_tag.get_text(strip=True),
                    "url": url,
                    "snippet": snippet_tag.get_text(strip=True) if snippet_tag else "",
                }
            )
            if len(results) >= max_results:
                break
        return results
    except ImportError:
        logger.debug("BeautifulSoup not available for httpx fallback")
        return []
    except Exception as exc:
        logger.debug("httpx fallback parse failed: %s", exc)
        return []


# ---------------------------------------------------------------------------
# Public tool
# ---------------------------------------------------------------------------


class WebSearchTool:
    """Search the web via DuckDuckGo with automatic fallback."""

    def __init__(self, max_results: int = 5, timeout: int = 10):
        self.max_results = max_results
        self.timeout = timeout
        self._ddgs: Any = None
        self._ddgs_available: Optional[bool] = None

    def _client(self) -> Any:
        if self._ddgs_available is False:
            return None
        if self._ddgs is not None:
            return self._ddgs

        DDGSClass = _import_ddgs()
        if DDGSClass is None:
            self._ddgs_available = False
            return None

        try:
            self._ddgs = DDGSClass(timeout=self.timeout)
            self._ddgs_available = True
            return self._ddgs
        except Exception as exc:
            logger.debug("DDGS init failed: %s", exc)
            self._ddgs_available = False
            return None

    def search(
        self, query: str, max_results: Optional[int] = None
    ) -> list[dict[str, str]]:
        """Return ``[{title, url, snippet}, ...]``.

        Tries the DDGS package first, then falls back to httpx scraping.
        """
        n = max_results or self.max_results

        client = self._client()
        if client is not None:
            try:
                raw = list(client.text(query, max_results=n))
                logger.info("WebSearch: %d results for %r (ddgs)", len(raw), query)
                return [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", ""),
                    }
                    for r in raw
                ]
            except Exception as exc:
                logger.debug("DDGS search failed, trying httpx fallback: %s", exc)

        results = _httpx_search(query, n, self.timeout)
        if results:
            logger.info("WebSearch: %d results for %r (httpx)", len(results), query)
        return results

    def search_text(self, query: str, max_results: Optional[int] = None) -> str:
        """Search and return a human-readable text block."""
        results = self.search(query, max_results)
        if not results:
            return ""
        lines: list[str] = []
        for i, r in enumerate(results, 1):
            lines.append(f"[{i}] {r['title']}")
            if r["snippet"]:
                lines.append(f"    {r['snippet']}")
            if r["url"]:
                lines.append(f"    Source: {r['url']}")
        return "\n".join(lines)
