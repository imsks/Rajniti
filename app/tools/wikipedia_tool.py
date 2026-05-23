"""
Wikipedia lookup tool — MediaWiki query + REST summary + outbound links.

Supports a rich ``politician_wikipedia_bundle()`` for citation context (extract,
canonical article URL, filtered external links).
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote, urlparse

import httpx

logger = logging.getLogger(__name__)

_API = "https://en.wikipedia.org/w/api.php"
_REST = "https://en.wikipedia.org/api/rest_v1"
_HEADERS = {
    "User-Agent": "Rajniti/1.0 (https://github.com/rajniti; bot@rajniti.dev)",
    "Accept": "application/json",
}


def _encode_title_for_rest_path(title: str) -> str:
    """Normalize for REST ``page/summary/{title}``: spaces→underscores, encode reserved."""
    t = title.strip().replace(" ", "_")
    return quote(t, safe="()+.-_~,!*':")


_STOPWORDS = frozenset(
    {
        "the",
        "and",
        "for",
        "was",
        "his",
        "her",
        "has",
        "have",
        "from",
        "that",
        "with",
        "who",
        "also",
        "been",
        "are",
        "not",
        "but",
        "its",
        "their",
        "they",
        "she",
        "him",
        "had",
        "will",
        "into",
        "over",
        "such",
        "other",
    }
)


def summary_matches_wikipedia_extract(summary: str, extract: str) -> bool:
    """Cheap overlap check — avoids anchoring summary_citation to the wrong bio."""
    if not (summary or "").strip() or not (extract or "").strip():
        return False
    sum_l = summary.lower().strip()
    ext_l = extract.lower().strip()
    if sum_l[:80] and sum_l[:80] in ext_l:
        return True
    if ext_l.startswith(sum_l[: min(120, len(sum_l))]):
        return True

    def toks(text: str) -> set[str]:
        return {
            m.group(0)
            for m in re.finditer(r"[a-z0-9]{3,}", text.lower())
            if m.group(0) not in _STOPWORDS
        }

    st = toks(sum_l)
    et = toks(ext_l)
    if not st:
        return False
    inter = len(st & et)
    if inter >= max(2, len(st) // 2):
        return True
    if inter / len(st) >= 0.45:
        return True
    return False


def _filter_external_links(raw: Optional[List[str]], limit: int) -> List[str]:
    if not raw:
        return []
    seen = set()
    out: List[str] = []
    for link in raw:
        if not link or not isinstance(link, str):
            continue
        link = link.strip()
        parsed = urlparse(link)
        if parsed.scheme not in ("http", "https"):
            continue
        host = (parsed.hostname or "").lower()
        if any(m in host for m in ("wikipedia.org", "wikimedia.org")):
            continue
        if link in seen:
            continue
        seen.add(link)
        out.append(link)
        if len(out) >= limit:
            break
    return out


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

    def summary_payload(self, title: str) -> Optional[dict[str, Any]]:
        """REST ``page/summary`` JSON (extract, ``content_urls``, etc.) or ``None``."""
        if not title or not title.strip():
            return None
        encoded = _encode_title_for_rest_path(title)
        try:
            resp = httpx.get(
                f"{_REST}/page/summary/{encoded}",
                headers=_HEADERS,
                timeout=self.timeout,
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.warning("Wikipedia summary_payload failed for %r: %s", title, exc)
            return None

    def summary(self, title: str) -> Optional[str]:
        """Fetch the plain-text extract of a Wikipedia article."""
        payload = self.summary_payload(title)
        if not payload:
            return None
        return payload.get("extract")

    def search_and_summarize(self, query: str) -> Optional[str]:
        """Search Wikipedia and return the summary of the best match."""
        hits = self.search(query, limit=1)
        if not hits:
            return None
        return self.summary(hits[0]["title"])

    def external_links_for_title(self, title: str, limit: int = 25) -> List[str]:
        """Outbound ``prop=parse|externallinks`` URLs for a page title."""
        if not title or not title.strip():
            return []
        try:
            resp = httpx.get(
                _API,
                params={
                    "action": "parse",
                    "page": title,
                    "prop": "externallinks",
                    "format": "json",
                },
                headers=_HEADERS,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            links = (data.get("parse") or {}).get("externallinks") or []
            return _filter_external_links(list(links), limit=limit)
        except Exception as exc:
            logger.warning("Wikipedia externallinks failed for %r: %s", title, exc)
            return []

    def politician_wikipedia_bundle(
        self, name: str, state: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Search + summary + outbound links suitable for citation context."""
        query = f"{name} Indian politician"
        if state:
            query += f" {state}"
        hits = self.search(query, limit=1)
        if not hits:
            return None
        title = hits[0]["title"]
        payload = self.summary_payload(title)
        if not payload:
            return None
        extract = payload.get("extract") or ""
        article_url = (payload.get("content_urls") or {}).get("desktop", {}).get("page")
        ext = self.external_links_for_title(title, limit=25)
        return {
            "title": title,
            "article_url": article_url,
            "extract": extract,
            "external_links": ext,
        }

    def politician_context(self, name: str, state: str = "", party: str = "") -> str:
        """Build a context block about an Indian politician from Wikipedia."""
        bundle = self.politician_wikipedia_bundle(name, state)
        if not bundle or not bundle.get("extract"):
            return ""
        return f"Wikipedia: {bundle['extract']}"

    def prune_misaligned_wikipedia_summary_citation(
        self,
        politician: Dict[str, Any],
        updates: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Drop ``political_background.summary_citation`` if URL is Wikipedia but summary ≠ extract overlap."""
        extra: List[str] = []
        pb_u = updates.get("political_background")
        if not isinstance(pb_u, dict):
            return updates, extra
        sc = pb_u.get("summary_citation")
        link = ""
        if isinstance(sc, dict):
            link = (sc.get("link") or "").strip().lower()

        if "wikipedia.org" not in link:
            return updates, extra

        stored_summary = (
            (politician.get("political_background") or {}).get("summary") or ""
        ).strip()

        bundle = self.politician_wikipedia_bundle(
            str(politician.get("name") or ""),
            str(politician.get("state") or ""),
        )
        extract = (bundle or {}).get("extract") or ""
        if (
            stored_summary
            and extract
            and summary_matches_wikipedia_extract(stored_summary, extract)
        ):
            return updates, extra

        issues_msg = (
            "summary_citation removed: Wikipedia bio does not align with stored summary "
            "or Wikipedia bundle unavailable"
        )
        extra.append(issues_msg)
        pb2 = dict(pb_u)
        pb2.pop("summary_citation", None)
        out = dict(updates)
        # If political_background ends up redundant (only citation removed), keep other keys merges sent
        out["political_background"] = pb2
        return out, extra
