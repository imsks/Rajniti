"""MyNeta candidate URL resolution via browser-use agent."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class MyNetaResolveResult:
    url: Optional[str] = None
    candidate_id: Optional[str] = None
    election_slug: Optional[str] = None
    raw_result: Optional[str] = None


def build_search_url(election_slug: str) -> str:
    slug = election_slug.strip("/")
    return f"https://www.myneta.info/{slug}/"


def build_resolve_instructions(
    name: str,
    state: str,
    constituency: str,
    election_slug: str,
) -> str:
    return (
        f"Search MyNeta for candidate '{name}' from constituency "
        f"'{constituency}' in state '{state}' for election '{election_slug}'. "
        "Navigate to their candidate.php profile page. "
        "When found, call done with raw JSON only (no markdown): "
        '{"url":"https://www.myneta.info/.../candidate.php?candidate_id=NNN",'
        f'"candidate_id":"NNN","election_slug":"{election_slug}"}}'
    )


def parse_resolve_result(text: str, election_slug: str) -> MyNetaResolveResult:
    text = (text or "").strip()
    if not text:
        return MyNetaResolveResult(raw_result=text)

    try:
        data = json.loads(text)
        if isinstance(data, dict) and data.get("url"):
            return MyNetaResolveResult(
                url=str(data["url"]),
                candidate_id=str(data.get("candidate_id") or ""),
                election_slug=str(data.get("election_slug") or election_slug),
                raw_result=text,
            )
    except json.JSONDecodeError:
        pass

    url_match = re.search(
        r"(https?://[^\s\"']+candidate\.php\?candidate_id=(\d+))",
        text,
        re.I,
    )
    if url_match:
        return MyNetaResolveResult(
            url=url_match.group(1),
            candidate_id=url_match.group(2),
            election_slug=election_slug,
            raw_result=text,
        )
    return MyNetaResolveResult(raw_result=text)
