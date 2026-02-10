"""
HTTP client for ECI website scraping.

Handles HTTP/2 connections, retries with exponential backoff, and
browser-like headers required by the ECI website.
"""

import logging
import time
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Browser-like headers required by ECI
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

_client: Optional[httpx.Client] = None


def _get_client() -> httpx.Client:
    """Get or create a shared HTTP/2 client. ECI blocks HTTP/1.1."""
    global _client
    if _client is None:
        _client = httpx.Client(
            http2=True,
            follow_redirects=True,
            timeout=30.0,
            headers=_HEADERS,
        )
    return _client


def fetch_page(
    url: str,
    *,
    referer: Optional[str] = None,
    retries: int = 3,
    timeout: int = 30,
) -> Optional[bytes]:
    """
    Fetch a page with retry logic and exponential backoff.

    Args:
        url: URL to fetch
        referer: Optional referer header (enables same-origin mode)
        retries: Number of retry attempts
        timeout: Request timeout in seconds

    Returns:
        Raw HTML bytes, or None if all retries fail
    """
    client = _get_client()
    headers = _HEADERS.copy()

    if referer:
        headers["Referer"] = referer
        headers["Sec-Fetch-Site"] = "same-origin"

    for attempt in range(retries):
        try:
            logger.info("Fetching: %s (attempt %d)", url, attempt + 1)
            response = client.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            logger.info("✓ Success (HTTP/%s)", response.http_version)
            time.sleep(0.5)  # polite delay
            return response.content

        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Attempt %d failed: %s %s",
                attempt + 1,
                exc.response.status_code,
                exc.response.reason_phrase,
            )
        except httpx.RequestError as exc:
            logger.warning("Attempt %d failed: %s", attempt + 1, exc)

        if attempt < retries - 1:
            wait = 2 * (attempt + 1) ** 1.5
            logger.info("Waiting %.1fs before retry...", wait)
            time.sleep(wait)

    logger.error("All retries exhausted for %s", url)
    return None


def normalize_base_url(url: str) -> str:
    """
    Strip trailing index files and slashes from a URL.

    Examples:
        >>> normalize_base_url("https://results.eci.gov.in/PcResultGenJune2024/index.htm")
        'https://results.eci.gov.in/PcResultGenJune2024'
    """
    url = url.rstrip("/")
    for suffix in ("/index.htm", "/index.html", "/default.htm", "/default.html"):
        if url.lower().endswith(suffix):
            url = url[: -len(suffix)]
            break
    return url
