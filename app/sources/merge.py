"""Field-level merge with explicit source precedence."""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional

from app.sources.base import SourceResult

# Higher number wins for structured facts from sources.
SOURCE_PRIORITY = {
    "eci": 30,
    "myneta": 20,
    "llm": 10,
}

_CITATION_RANK = {
    "ECI": 4,
    "MYNETA": 3,
    "GOV_WEBSITE": 2,
    "NEWS": 1,
    "OTHERS": 0,
}


def _citation_rank(citation: Any) -> int:
    if not citation or not isinstance(citation, dict):
        return -1
    src = citation.get("source")
    if not src:
        return -1
    return _CITATION_RANK.get(str(src), 0)


def _merge_citation(existing: Any, incoming: Any) -> Any:
    if incoming is None:
        return existing
    if existing is None:
        return incoming
    if _citation_rank(incoming) >= _citation_rank(existing):
        return incoming
    return existing


def _merge_list_by_index(
    existing: Optional[List[Any]],
    incoming: Optional[List[Any]],
    *,
    prefer_incoming: bool,
) -> Optional[List[Any]]:
    if not incoming:
        return existing
    if not existing:
        return copy.deepcopy(incoming)
    if prefer_incoming:
        merged = copy.deepcopy(incoming)
        # Preserve extra existing rows beyond incoming length.
        if len(existing) > len(incoming):
            merged.extend(copy.deepcopy(existing[len(incoming) :]))
        return merged
    merged = copy.deepcopy(existing)
    for idx, inc in enumerate(incoming):
        if idx >= len(merged):
            merged.append(copy.deepcopy(inc))
            continue
        cur = merged[idx]
        if not isinstance(cur, dict) or not isinstance(inc, dict):
            merged[idx] = copy.deepcopy(inc)
            continue
        row = copy.deepcopy(cur)
        for key, val in inc.items():
            if key == "citation":
                row["citation"] = _merge_citation(cur.get("citation"), val)
            elif val not in (None, "", []):
                if prefer_incoming or not row.get(key):
                    row[key] = val
        merged[idx] = row
    return merged


def _merge_dict_maps(
    existing: Optional[Dict[str, Any]],
    incoming: Optional[Dict[str, Any]],
    *,
    prefer_incoming: bool,
) -> Optional[Dict[str, Any]]:
    if not incoming:
        return existing
    out = copy.deepcopy(existing or {})
    for key, val in incoming.items():
        if val is None:
            continue
        if prefer_incoming or key not in out or not out[key]:
            out[key] = val
        elif isinstance(val, dict) and isinstance(out.get(key), dict):
            if _citation_rank(val) > _citation_rank(out[key]):
                out[key] = val
    return out or None


def _merge_financial_disclosure(
    existing: Optional[Dict[str, Any]], incoming: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    if not incoming:
        return existing
    if not existing:
        return copy.deepcopy(incoming)
    out = copy.deepcopy(existing)
    for key in (
        "total_assets_inr",
        "total_liabilities_inr",
        "net_worth_inr",
        "as_of_election",
        "movable_assets",
        "immovable_assets",
        "liabilities",
        "citation",
    ):
        inc_val = incoming.get(key)
        if inc_val in (None, "", []):
            continue
        if key == "citation":
            out["citation"] = _merge_citation(out.get("citation"), inc_val)
        else:
            out[key] = inc_val
    return out


def _merge_political_background(
    existing: Optional[Dict[str, Any]],
    incoming: Optional[Dict[str, Any]],
    *,
    prefer_incoming_elections: bool,
) -> Optional[Dict[str, Any]]:
    if not incoming:
        return existing
    out = copy.deepcopy(existing or {})
    elections = _merge_list_by_index(
        (existing or {}).get("elections"),
        incoming.get("elections"),
        prefer_incoming=prefer_incoming_elections,
    )
    if elections is not None:
        out["elections"] = elections
    for key in ("summary", "summary_citation"):
        inc = incoming.get(key)
        if inc in (None, ""):
            continue
        if key == "summary_citation":
            out[key] = _merge_citation(out.get(key), inc)
        elif not out.get(key):
            out[key] = inc
    return out


def merge_source_results(
    base: Dict[str, Any],
    results: List[SourceResult],
) -> Dict[str, Any]:
    """Merge ordered source results into a politician dict."""
    merged = copy.deepcopy(base)
    issues: List[str] = []

    ordered = sorted(results, key=lambda r: r.priority, reverse=True)

    for result in ordered:
        issues.extend(result.issues)
        data = result.data
        priority = result.priority
        prefer = priority >= SOURCE_PRIORITY["myneta"]
        prefer_elections = priority >= SOURCE_PRIORITY["eci"]

        if "financial_disclosure" in data:
            merged["financial_disclosure"] = _merge_financial_disclosure(
                merged.get("financial_disclosure"), data.get("financial_disclosure")
            )

        if "education" in data:
            merged["education"] = _merge_list_by_index(
                merged.get("education"),
                data.get("education"),
                prefer_incoming=prefer,
            )

        if "criminal_records" in data:
            merged["criminal_records"] = _merge_list_by_index(
                merged.get("criminal_records"),
                data.get("criminal_records"),
                prefer_incoming=prefer,
            )

        if "political_background" in data:
            merged["political_background"] = _merge_political_background(
                merged.get("political_background"),
                data.get("political_background"),
                prefer_incoming_elections=prefer_elections,
            )

        if "source_sync" in data:
            sync = copy.deepcopy(merged.get("source_sync") or {})
            sync.update(data["source_sync"])
            merged["source_sync"] = sync

        for key in ("social_media", "contact", "family_background"):
            if key in data:
                merged[key] = data[key] if prefer else (merged.get(key) or data.get(key))

        for key in (
            "contact_citations",
            "social_media_citations",
            "performance_citations",
        ):
            if key in data:
                merged[key] = _merge_dict_maps(
                    merged.get(key), data.get(key), prefer_incoming=prefer
                )

    if issues:
        audit = copy.deepcopy(merged.get("citation_audit") or {})
        existing_issues = list(audit.get("issues") or [])
        audit["issues"] = existing_issues + issues
        merged["citation_audit"] = audit

    return merged
