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


def politician_citation_coverage_pct(politician: Dict[str, Any]) -> Optional[float]:
    """Percentage of citation slots that already have a citation (0–100).

    Mirrors the inventory used by ``politician_needs_citation_audit``. Returns
    ``None`` when there are no slots (nothing to cite).
    """
    total = 0
    filled = 0

    for row in politician.get("education") or []:
        if isinstance(row, dict):
            total += 1
            if row.get("citation"):
                filled += 1

    pb = politician.get("political_background") or {}
    if (pb.get("summary") or "").strip():
        total += 1
        if pb.get("summary_citation"):
            filled += 1

    for ev in pb.get("elections") or []:
        if isinstance(ev, dict):
            total += 1
            if ev.get("citation"):
                filled += 1

    for row in politician.get("family_background") or []:
        if isinstance(row, dict):
            total += 1
            if row.get("citation"):
                filled += 1

    for row in politician.get("criminal_records") or []:
        if isinstance(row, dict):
            total += 1
            if row.get("citation"):
                filled += 1

    contact = politician.get("contact") or {}
    cc = politician.get("contact_citations") or {}
    for k in _CONTACT_KEYS:
        if contact.get(k):
            total += 1
            if k in cc:
                filled += 1

    sm = politician.get("social_media") or {}
    smc = politician.get("social_media_citations") or {}
    for k in _SOCIAL_KEYS:
        if sm.get(k):
            total += 1
            if k in smc:
                filled += 1

    if politician.get("type") == "MP":
        perf = politician.get("performance") or {}
        pc = politician.get("performance_citations") or {}
        for k in _PERF_KEYS:
            if perf.get(k) is not None:
                total += 1
                if k in pc:
                    filled += 1

    if total == 0:
        return None
    return round(100.0 * filled / total, 6)


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
                k
                for k in _PERF_KEYS
                if perf.get(k) is not None and k not in pc
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
