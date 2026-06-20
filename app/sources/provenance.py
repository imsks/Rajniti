"""Helpers for citation provenance and source-aware agent gating."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

PRIMARY_SOURCES = frozenset({"ECI", "MYNETA", "GOV_WEBSITE"})


def citation_source(citation: Any) -> Optional[str]:
    if not citation or not isinstance(citation, dict):
        return None
    src = citation.get("source")
    return str(src) if src else None


def has_citation_from(items: Optional[Iterable[Any]], source: str) -> bool:
    if not items:
        return False
    for item in items:
        if not isinstance(item, dict):
            continue
        if citation_source(item.get("citation")) == source:
            return True
    return False


def has_primary_citations(items: Optional[Iterable[Any]]) -> bool:
    if not items:
        return False
    for item in items:
        if not isinstance(item, dict):
            continue
        src = citation_source(item.get("citation"))
        if src in PRIMARY_SOURCES:
            return True
    return False


def elections_have_eci_citations(politician: Dict[str, Any]) -> bool:
    elections = (politician.get("political_background") or {}).get("elections") or []
    if not elections:
        return False
    return all(
        isinstance(e, dict) and citation_source(e.get("citation")) == "ECI"
        for e in elections
    )
