"""MyNeta affidavit source — browser-use extracts from page; we validate only."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.browser.parsing import parse_agent_json_object
from app.schemas.politician import (
    CitationSource,
    CrimeRecord,
    Education,
    FinancialDisclosure,
)
from app.sources.base import SourceResult
from app.sources.merge import SOURCE_PRIORITY

NAME = "myneta"
PRIORITY = SOURCE_PRIORITY[NAME]

_ELECTIONS_PATH = Path(__file__).resolve().parents[1] / "data" / "myneta_elections.json"
_ELECTIONS_CACHE: Optional[Dict[str, Any]] = None


class MyNetaAgentResult(BaseModel):
    """Structured output browser-use must fill from the candidate profile page."""

    financial_disclosure: FinancialDisclosure
    education: Optional[List[Education]] = None
    criminal_records: Optional[List[CrimeRecord]] = None


def _load_elections_map() -> Dict[str, Any]:
    global _ELECTIONS_CACHE
    if _ELECTIONS_CACHE is None:
        with _ELECTIONS_PATH.open(encoding="utf-8") as f:
            _ELECTIONS_CACHE = json.load(f)
    return _ELECTIONS_CACHE


def election_slug_for(
    politician_type: str,
    state: str,
    *,
    year: Optional[int] = None,
) -> Optional[str]:
    data = _load_elections_map()
    by_type = data.get(politician_type.upper()) or {}
    entry = by_type.get(state)
    if not entry:
        return None
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        if year and str(year) in entry:
            return entry[str(year)]
        if "default" in entry:
            return entry["default"]
        year_keys = [k for k in entry if k.isdigit()]
        if year_keys:
            return entry[max(year_keys, key=int)]
    return None


def _profile_url(politician: Dict[str, Any]) -> Optional[str]:
    fd = politician.get("financial_disclosure") or {}
    cite = fd.get("citation") or {}
    link = cite.get("link")
    if link and "myneta" in str(link).lower():
        return str(link)
    for section in ("education", "criminal_records"):
        for item in politician.get(section) or []:
            if not isinstance(item, dict):
                continue
            c = item.get("citation") or {}
            if c.get("source") == CitationSource.MYNETA.value and c.get("link"):
                return str(c["link"])
    return None


def _latest_election_year(politician: Dict[str, Any]) -> Optional[int]:
    elections = (politician.get("political_background") or {}).get("elections") or []
    years = [e.get("year") for e in elections if isinstance(e, dict) and e.get("year")]
    return max(years) if years else None


def _election_slug(politician: Dict[str, Any]) -> Optional[str]:
    url = _profile_url(politician)
    if url:
        import re

        m = re.search(r"myneta\.info/([^/]+)/", url, re.I)
        if m:
            return m.group(1)
    return election_slug_for(
        str(politician.get("type") or "MLA"),
        str(politician.get("state") or ""),
        year=_latest_election_year(politician),
    )


def can_fetch(politician: Dict[str, Any], *, force: bool = False) -> bool:
    if force:
        return True
    sync = politician.get("source_sync") or {}
    if sync.get(NAME) and _profile_url(politician):
        return False
    return bool(_election_slug(politician))


def _build_extract_instructions(
    politician: Dict[str, Any],
    election_slug: str,
    *,
    profile_url: Optional[str] = None,
) -> str:
    cite_hint = (
        'Every field needs citation {"link": "<candidate.php URL you opened>", "source": "MYNETA"}.'
    )
    if profile_url:
        return (
            f"This is the candidate profile at {profile_url}. "
            "Read assets, liabilities, education, and criminal cases from the page. "
            f"{cite_hint}"
        )
    return (
        f"Find candidate '{politician.get('name')}' in constituency "
        f"'{politician.get('constituency')}' ({politician.get('state')}, election {election_slug}). "
        "Open their candidate.php profile on myneta.info. "
        "Read assets, liabilities, education, and criminal cases from that page. "
        f"{cite_hint}"
    )


def validate_agent_result(raw: str) -> MyNetaAgentResult:
    """Parse + validate JSON (tests / fallbacks). Production uses browser structured output."""
    return MyNetaAgentResult.model_validate(parse_agent_json_object(raw))


def fetch(politician: Dict[str, Any], *, force: bool = False) -> SourceResult:
    from app.browser import run_browser_extract
    from app.browser.scraper import run_scrape_agent
    from app.sources.myneta_resolve import (
        build_resolve_instructions,
        build_search_url,
        parse_resolve_result,
    )

    election_slug = _election_slug(politician)
    if not election_slug:
        raise ValueError(
            f"No election slug for {politician.get('state')} {politician.get('type')}"
        )

    known_url = None if force else _profile_url(politician)
    start_url = known_url
    if not start_url:
        search_url = build_search_url(election_slug)
        resolve_instructions = build_resolve_instructions(
            str(politician.get("name") or ""),
            str(politician.get("state") or ""),
            str(politician.get("constituency") or ""),
            election_slug,
        )
        resolve_result = run_scrape_agent(search_url, resolve_instructions)
        parsed = parse_resolve_result(resolve_result.result, election_slug)
        if not parsed.url:
            snippet = (resolve_result.result or "")[:500]
            raise ValueError(f"Could not resolve MyNeta profile URL: {snippet}")
        start_url = parsed.url

    instructions = _build_extract_instructions(
        politician, election_slug, profile_url=start_url
    )

    extracted = run_browser_extract(
        start_url,
        instructions,
        output_model=MyNetaAgentResult,
    )

    data = extracted.data.model_dump(mode="json", exclude_none=True)
    data["source_sync"] = {NAME: datetime.now(timezone.utc).isoformat()}

    issues: list[str] = []
    fd = data.get("financial_disclosure") or {}
    if not fd.get("total_assets_inr") and not data.get("education"):
        issues.append("Browser extraction yielded minimal affidavit fields")
    if extracted.steps_taken < 2:
        issues.append(f"Only {extracted.steps_taken} browser step(s) — verify page was read")

    return SourceResult(source_name=NAME, data=data, priority=PRIORITY, issues=issues)
