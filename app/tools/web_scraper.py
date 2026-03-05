"""
Lightweight web-page scraper — extracts readable text from a URL.

Uses ``httpx`` + ``beautifulsoup4`` (both already in requirements.txt).
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

_STRIP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "noscript"}


class WebScraperTool:
    """Fetch a URL and return its main text content."""

    def __init__(self, timeout: int = 15, max_chars: int = 5000):
        self.timeout = timeout
        self.max_chars = max_chars

    def fetch_text(self, url: str) -> Optional[str]:
        """Return cleaned text from *url*, or ``None`` on any failure."""
        try:
            resp = httpx.get(
                url,
                headers={"User-Agent": _UA},
                timeout=self.timeout,
                follow_redirects=True,
            )
            resp.raise_for_status()
        except Exception as exc:
            logger.warning("WebScraper: fetch failed %s — %s", url, exc)
            return None

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(_STRIP_TAGS):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
            text = "\n".join(lines)

            if len(text) > self.max_chars:
                text = text[: self.max_chars] + "…"
            return text
        except Exception as exc:
            logger.warning("WebScraper: parse failed %s — %s", url, exc)
            return None
