"""Merge citation-only LLM audit results into politician update dicts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.politician import CitationAuditLLMResult

_CONTACT_KEYS = frozenset({"email", "phone", "address"})
_SOCIAL_KEYS = frozenset(
    {"twitter", "facebook", "instagram", "linkedin", "youtube", "website"}
)
_PERF_KEYS = frozenset({"attendance", "questions", "debates"})

# Skip LLM when this fraction (percent) or more of citation slots already have URLs.
CITATION_COVERAGE_SKIP_THRESHOLD_PCT = 40


# The profile hero's badge groups checkable fields into these tabs/categories.
# "performance" is added on top of this list only when it applies (MP with a
# recorded stat) — MLAs, and MPs without performance data, never have it.
_REQUIRED_CATEGORIES = ("education", "history", "family", "criminal", "contact")


def politician_citation_coverage_summary(politician: Dict[str, Any]) -> Dict[str, Any]:
    """Fractional citation coverage, raw counts, and category completeness.

    The auto-generated ``political_background.summary`` is excluded — it is
    synthesized from the election records already counted below, not an
    independent fact, so counting it would inflate coverage for thin profiles.

    ``categories_mostly_present`` is True once all but at most one of the
    profile's hero-tab categories (Education, History, Family, Criminal,
    Contact, and Performance when applicable) has at least one checkable
    item — the badge only shows a percentage once the profile is broadly
    filled in, not just well-cited on a couple of thin categories.
    """
    total = 0
    filled = 0
    category_present: Dict[str, bool] = {}

    edu_total = sum(1 for row in politician.get("education") or [] if isinstance(row, dict))
    edu_filled = sum(
        1 for row in politician.get("education") or [] if isinstance(row, dict) and row.get("citation")
    )
    total += edu_total
    filled += edu_filled
    category_present["education"] = edu_total > 0

    pb = politician.get("political_background") or {}
    elections = [ev for ev in pb.get("elections") or [] if isinstance(ev, dict)]
    hist_total = len(elections)
    hist_filled = sum(1 for ev in elections if ev.get("citation"))
    total += hist_total
    filled += hist_filled
    category_present["history"] = hist_total > 0

    family = [row for row in politician.get("family_background") or [] if isinstance(row, dict)]
    fam_total = len(family)
    fam_filled = sum(1 for row in family if row.get("citation"))
    total += fam_total
    filled += fam_filled
    category_present["family"] = fam_total > 0

    criminal = [row for row in politician.get("criminal_records") or [] if isinstance(row, dict)]
    cr_total = len(criminal)
    cr_filled = sum(1 for row in criminal if row.get("citation"))
    total += cr_total
    filled += cr_filled
    category_present["criminal"] = cr_total > 0

    contact = politician.get("contact") or {}
    cc = politician.get("contact_citations") or {}
    sm = politician.get("social_media") or {}
    smc = politician.get("social_media_citations") or {}
    contact_total = 0
    contact_filled = 0
    for k in _CONTACT_KEYS:
        if contact.get(k):
            contact_total += 1
            if k in cc:
                contact_filled += 1
    for k in _SOCIAL_KEYS:
        if sm.get(k):
            contact_total += 1
            if k in smc:
                contact_filled += 1
    total += contact_total
    filled += contact_filled
    category_present["contact"] = contact_total > 0

    required = list(_REQUIRED_CATEGORIES)
    if politician.get("type") == "MP":
        perf = politician.get("performance") or {}
        pc = politician.get("performance_citations") or {}
        if any(perf.get(k) not in (None, 0, "") for k in _PERF_KEYS):
            perf_total = sum(1 for k in _PERF_KEYS if perf.get(k) is not None)
            perf_filled = sum(1 for k in _PERF_KEYS if perf.get(k) is not None and k in pc)
            total += perf_total
            filled += perf_filled
            category_present["performance"] = perf_total > 0
            required.append("performance")

    present_count = sum(1 for c in required if category_present.get(c))
    categories_mostly_present = present_count >= len(required) - 1

    return {
        "cited_fields_count": filled,
        "checkable_fields_count": total,
        "sourced_pct": None if total == 0 else round(filled / total, 6),
        "categories_mostly_present": categories_mostly_present,
    }


def politician_citation_coverage_pct(politician: Dict[str, Any]) -> Optional[float]:
    """Percentage of citation slots that already have a citation (0–100).

    Mirrors the inventory used by ``politician_needs_citation_audit``. Returns
    ``None`` when there are no slots (nothing to cite).
    """
    summary = politician_citation_coverage_summary(politician)
    sourced_pct = summary["sourced_pct"]
    if sourced_pct is None:
        return None
    return round(100.0 * sourced_pct, 6)


def _collect_politician_citation_gaps(politician: Dict[str, Any]) -> Dict[str, Any]:
    """Citation slots lacking URLs (canonical inventory = coverage / needs_audit)."""
    gaps: Dict[str, Any] = {}

    edu_idx = [
        i
        for i, row in enumerate(politician.get("education") or [])
        if isinstance(row, dict) and not row.get("citation")
    ]
    if edu_idx:
        gaps["education_indices"] = edu_idx

    pb = politician.get("political_background") or {}
    if (pb.get("summary") or "").strip() and not pb.get("summary_citation"):
        gaps["summary_needs_citation"] = True

    el_idx = [
        i
        for i, ev in enumerate(pb.get("elections") or [])
        if isinstance(ev, dict) and not ev.get("citation")
    ]
    if el_idx:
        gaps["elections_indices"] = el_idx

    fam_idx = [
        i
        for i, row in enumerate(politician.get("family_background") or [])
        if isinstance(row, dict) and not row.get("citation")
    ]
    if fam_idx:
        gaps["family_indices"] = fam_idx

    cr_idx = [
        i
        for i, row in enumerate(politician.get("criminal_records") or [])
        if isinstance(row, dict) and not row.get("citation")
    ]
    if cr_idx:
        gaps["criminal_indices"] = cr_idx

    contact = politician.get("contact") or {}
    cc = politician.get("contact_citations") or {}
    ck = sorted(k for k in _CONTACT_KEYS if contact.get(k) and k not in cc)
    if ck:
        gaps["contact_keys"] = ck

    sm = politician.get("social_media") or {}
    smc = politician.get("social_media_citations") or {}
    sk = sorted(k for k in _SOCIAL_KEYS if sm.get(k) and k not in smc)
    if sk:
        gaps["social_media_keys"] = sk

    if politician.get("type") == "MP":
        perf = politician.get("performance") or {}
        pc = politician.get("performance_citations") or {}
        if any(perf.get(k) not in (None, 0, "") for k in _PERF_KEYS):
            pk = sorted(
                k for k in _PERF_KEYS if perf.get(k) is not None and k not in pc
            )
            if pk:
                gaps["performance_keys"] = pk

    return gaps


def politician_citation_gaps(politician: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Structured backlog: indices/keys lacking citations. ``None`` if fully cited on this inventory."""
    raw = _collect_politician_citation_gaps(politician)
    return raw if raw else None


def politician_needs_citation_audit(politician: Dict[str, Any]) -> bool:
    """True if any present detail field lacks a citation."""
    return bool(_collect_politician_citation_gaps(politician))


def merge_citation_audit_updates(
    politician: Dict[str, Any], audit: CitationAuditLLMResult
) -> Tuple[Dict[str, Any], List[str]]:
    """Build ``updates`` for PoliticianService.update_politician. Returns (updates, issues)."""
    updates: Dict[str, Any] = {}
    issues = list(audit.issues or [])

    if audit.education_citations and politician.get("education"):
        new_edu = [dict(x) for x in (politician.get("education") or [])]
        changed = False
        for i, cit in enumerate(audit.education_citations):
            if cit is None or i >= len(new_edu):
                continue
            if not new_edu[i].get("citation"):
                new_edu[i]["citation"] = cit.model_dump(mode="json")
                changed = True
        if changed:
            updates["education"] = new_edu

    pb = dict(politician.get("political_background") or {})
    pb_changed = False

    if audit.elections_citations and pb.get("elections"):
        new_elec = [dict(x) for x in pb["elections"]]
        changed = False
        for i, cit in enumerate(audit.elections_citations):
            if cit is None or i >= len(new_elec):
                continue
            if not new_elec[i].get("citation"):
                new_elec[i]["citation"] = cit.model_dump(mode="json")
                changed = True
        if changed:
            pb["elections"] = new_elec
            pb_changed = True

    if (
        audit.summary_citation
        and (pb.get("summary") or "").strip()
        and not pb.get("summary_citation")
    ):
        pb["summary_citation"] = audit.summary_citation.model_dump(mode="json")
        pb_changed = True

    if pb_changed:
        updates["political_background"] = pb

    if audit.family_citations and politician.get("family_background"):
        new_fam = [dict(x) for x in (politician.get("family_background") or [])]
        changed = False
        for i, cit in enumerate(audit.family_citations):
            if cit is None or i >= len(new_fam):
                continue
            if not new_fam[i].get("citation"):
                new_fam[i]["citation"] = cit.model_dump(mode="json")
                changed = True
        if changed:
            updates["family_background"] = new_fam

    if audit.criminal_citations and politician.get("criminal_records"):
        new_cr = [dict(x) for x in (politician.get("criminal_records") or [])]
        changed = False
        for i, cit in enumerate(audit.criminal_citations):
            if cit is None or i >= len(new_cr):
                continue
            if not new_cr[i].get("citation"):
                new_cr[i]["citation"] = cit.model_dump(mode="json")
                changed = True
        if changed:
            updates["criminal_records"] = new_cr

    if audit.contact_citations:
        contact = politician.get("contact") or {}
        cc = dict(politician.get("contact_citations") or {})
        for k, cit in audit.contact_citations.items():
            if cit is None:
                continue
            if k not in _CONTACT_KEYS:
                issues.append(f"ignored contact_citations key: {k}")
                continue
            if contact.get(k) and k not in cc:
                cc[k] = cit.model_dump(mode="json")
        if cc != (politician.get("contact_citations") or {}):
            updates["contact_citations"] = cc

    if audit.social_media_citations:
        sm = politician.get("social_media") or {}
        smc = dict(politician.get("social_media_citations") or {})
        for k, cit in audit.social_media_citations.items():
            if cit is None:
                continue
            if k not in _SOCIAL_KEYS:
                issues.append(f"ignored social_media_citations key: {k}")
                continue
            if sm.get(k) and k not in smc:
                smc[k] = cit.model_dump(mode="json")
        if smc != (politician.get("social_media_citations") or {}):
            updates["social_media_citations"] = smc

    if audit.performance_citations and politician.get("type") == "MP":
        perf = politician.get("performance") or {}
        pc = dict(politician.get("performance_citations") or {})
        for k, cit in audit.performance_citations.items():
            if cit is None:
                continue
            if k not in _PERF_KEYS:
                issues.append(f"ignored performance_citations key: {k}")
                continue
            if perf.get(k) is not None and k not in pc:
                pc[k] = cit.model_dump(mode="json")
        if pc != (politician.get("performance_citations") or {}):
            updates["performance_citations"] = pc

    meta_issues = [i for i in issues if i]
    if meta_issues or updates:
        audit_meta = dict(politician.get("citation_audit") or {})
        audit_meta["last_run"] = datetime.now(timezone.utc).isoformat()
        if meta_issues:
            audit_meta["issues"] = meta_issues
        updates["citation_audit"] = audit_meta

    return updates, issues
