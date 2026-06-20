from __future__ import annotations

import logging
from typing import Any, Dict, Literal, Optional

from pydantic import TypeAdapter

from app.agents.base_agent import BaseAgent
from app.core import CacheManager, log
from app.prompts import PoliticianPrompts
from app.schemas.politician import (
    Citation,
    Contact,
    CrimeRecord,
    Education,
    ElectionRecord,
    FamilyMember,
    PoliticalBackground,
    SocialMedia,
)
from app.services import PoliticianService
from app.sources.orchestrator import SourceOrchestrator
from app.sources.provenance import elections_have_eci_citations, has_primary_citations

logger = logging.getLogger(__name__)

DEFAULT_PIPELINE_SOURCES = ["myneta"]


def _is_llm_quota_exc(exc: BaseException) -> bool:
    msg = str(exc).lower()
    if "freetierllm" in msg and ("all candidates" in msg or "skipped or failed" in msg):
        return True
    if "resource exhausted" in msg:
        return True
    if "insufficient_quota" in msg or " rate limit" in msg:
        return True
    if "429" in msg:
        return True
    if "rajniti_llm_max_calls" in msg:
        return True
    return False


# ---------------------------------------------------------------------------
# Sub-processes (each enriches one field)
# ---------------------------------------------------------------------------


class PoliticianEducation:
    """Education enrichment process for one politician."""

    name = "education"

    def __init__(self, base_agent: BaseAgent):
        self.base = base_agent

    def should_run(self, politician: Dict[str, Any], force: bool = False) -> bool:
        if force:
            return True
        if has_primary_citations(politician.get("education")):
            return False
        edu = politician.get("education")
        if edu is None:
            return True
        if not edu:
            return False
        return any(not (isinstance(x, dict) and x.get("citation")) for x in edu)

    @log(logger, "PoliticianEducation.run")
    def run(
        self,
        politician: Dict[str, Any],
        force: bool = False,
        context: str = "",
    ) -> Dict[str, Any]:
        if not self.should_run(politician, force):
            return {
                "process": self.name,
                "ok": True,
                "skipped": True,
                "reason": "already_present",
            }

        prompt = PoliticianPrompts.education(politician)
        logger.info(
            "education: calling LLM (id=%s name=%s)",
            politician.get("id"),
            politician.get("name"),
        )
        raw = self.base._run_llm_with_context(prompt, context)
        parsed = self.base._parse_json_value(raw)

        if parsed is None:
            return {
                "process": self.name,
                "ok": False,
                "error": "invalid_llm_json",
                "raw": raw,
            }

        items = self.base._coerce_to_list(parsed)
        if items is None:
            return {
                "process": self.name,
                "ok": False,
                "error": "invalid_shape",
                "raw": raw,
            }

        adapter = TypeAdapter(list[Education])
        validated, errors = self.base._validate_with_adapter(items, adapter)
        if errors:
            return {
                "process": self.name,
                "ok": False,
                "error": "validation_failed",
                "details": errors,
            }

        if validated and any(item.citation is None for item in validated):
            return {
                "process": self.name,
                "ok": False,
                "error": "missing_citations",
            }

        updates = {"education": [item.model_dump(mode="json") for item in validated]}
        return {"process": self.name, "ok": True, "skipped": False, "updates": updates}


class PoliticianPoliticalBackground:
    """Political background enrichment process for one politician."""

    name = "political_background"

    def __init__(self, base_agent: BaseAgent):
        self.base = base_agent

    def should_run(self, politician: Dict[str, Any], force: bool = False) -> bool:
        if force:
            return True
        pb = politician.get("political_background") or {}
        elections = pb.get("elections") or []
        if not elections:
            return True
        if elections_have_eci_citations(politician):
            if (pb.get("summary") or "").strip() and not pb.get("summary_citation"):
                return True
            if not (pb.get("summary") or "").strip():
                return True
            return False
        if any(not (isinstance(e, dict) and e.get("citation")) for e in elections):
            return True
        if (pb.get("summary") or "").strip() and not pb.get("summary_citation"):
            return True
        return False

    @log(logger, "PoliticianPoliticalBackground.run")
    def run(
        self,
        politician: Dict[str, Any],
        force: bool = False,
        context: str = "",
    ) -> Dict[str, Any]:
        if not self.should_run(politician, force):
            return {
                "process": self.name,
                "ok": True,
                "skipped": True,
                "reason": "already_present",
            }

        prompt = PoliticianPrompts.political_background(politician)
        raw = self.base._run_llm_with_context(prompt, context)
        parsed = self.base._parse_json_object(raw)
        if parsed is None:
            return {
                "process": self.name,
                "ok": False,
                "error": "invalid_llm_json",
                "raw": raw,
            }

        adapter = TypeAdapter(PoliticalBackground)
        validated, errors = self.base._validate_with_adapter(parsed, adapter)
        updates: Dict[str, Any] = {}

        if not errors and validated is not None:
            if any(e.citation is None for e in validated.elections):
                return {
                    "process": self.name,
                    "ok": False,
                    "error": "missing_citations",
                    "details": "election record without citation",
                }
            if (validated.summary or "").strip() and validated.summary_citation is None:
                return {
                    "process": self.name,
                    "ok": False,
                    "error": "missing_citations",
                    "details": "summary without summary_citation",
                }
            updates["political_background"] = validated.model_dump(mode="json")
            logger.info(
                "political_background: full validation succeeded (id=%s)",
                politician.get("id"),
            )
            logger.debug("political_background: updates=%s", updates)
            if not updates["political_background"].get("elections"):
                self._maybe_fill_elections_only(politician, updates, context)
            return {
                "process": self.name,
                "ok": True,
                "skipped": False,
                "updates": updates,
            }

        validation_errors = errors
        partial_updates: Dict[str, Any] = {"elections": [], "summary": None}

        if isinstance(parsed.get("elections"), list):
            elections_adapter = TypeAdapter(list[ElectionRecord])
            ev_validated, ev_errors = self.base._validate_with_adapter(
                parsed.get("elections"), elections_adapter
            )
            if ev_validated is not None and not ev_errors:
                if any(e.citation is None for e in ev_validated):
                    logger.debug(
                        "political_background: elections missing citations (partial)"
                    )
                else:
                    partial_updates["elections"] = [
                        e.model_dump(mode="json") for e in ev_validated
                    ]
            else:
                logger.debug(
                    "political_background: elections validation failed: %s",
                    ev_errors,
                )

        summary_val = parsed.get("summary")
        if isinstance(summary_val, str) and summary_val.strip():
            partial_updates["summary"] = summary_val.strip()

        sc_raw = parsed.get("summary_citation")
        if isinstance(sc_raw, dict) and partial_updates.get("summary"):
            sc_ad = TypeAdapter(Citation | None)
            sc_val, sc_err = self.base._validate_with_adapter(sc_raw, sc_ad)
            if not sc_err and sc_val is not None:
                partial_updates["summary_citation"] = sc_val.model_dump(mode="json")

        if partial_updates["elections"] or partial_updates["summary"] is not None:
            updates["political_background"] = partial_updates
            logger.info(
                "political_background: partial acceptance (id=%s) errors=%s",
                politician.get("id"),
                validation_errors,
            )
            self._maybe_fill_elections_only(politician, updates, context)
            logger.debug("political_background: partial updates=%s", updates)
            return {
                "process": self.name,
                "ok": True,
                "skipped": False,
                "updates": updates,
                "validation_errors": validation_errors,
            }

        logger.warning(
            "political_background: validation failed (id=%s) errors=%s",
            politician.get("id"),
            validation_errors,
        )
        return {
            "process": self.name,
            "ok": False,
            "error": "validation_failed",
            "details": validation_errors,
        }

    def _maybe_fill_elections_only(
        self,
        politician: Dict[str, Any],
        updates: Dict[str, Any],
        context: str = "",
    ) -> None:
        """If elections are empty, issue a focused elections-only prompt and merge."""
        pb = updates.get("political_background") or {}
        if pb.get("elections"):
            return

        logger.info(
            "political_background: elections empty; issuing elections-only prompt (id=%s)",
            politician.get("id"),
        )
        prompt = PoliticianPrompts.political_background_elections_only(politician)
        raw = self.base._run_llm_with_context(prompt, context)
        parsed = self.base._parse_json_value(raw)
        if parsed is None:
            logger.warning(
                "political_background: elections-only prompt returned invalid JSON (id=%s)",
                politician.get("id"),
            )
            return

        elections_adapter = TypeAdapter(list[ElectionRecord])
        ev_validated, ev_errors = self.base._validate_with_adapter(
            parsed, elections_adapter
        )
        if ev_errors or ev_validated is None:
            logger.warning(
                "political_background: elections-only validation failed (id=%s) errors=%s",
                politician.get("id"),
                ev_errors,
            )
            return

        if any(e.citation is None for e in ev_validated):
            logger.warning(
                "political_background: elections-only missing citations (id=%s)",
                politician.get("id"),
            )
            return

        pb["elections"] = [e.model_dump(mode="json") for e in ev_validated]
        updates["political_background"] = pb
        logger.info(
            "political_background: elections-only prompt filled %d records (id=%s)",
            len(pb["elections"]),
            politician.get("id"),
        )


_SOCIAL_FIELDS = (
    "twitter",
    "facebook",
    "instagram",
    "linkedin",
    "youtube",
    "website",
)
_CONTACT_FIELDS = ("email", "phone", "address")


class PoliticianSocialMedia:
    """Social media enrichment process for one politician."""

    name = "social_media"

    def __init__(self, base_agent: BaseAgent):
        self.base = base_agent

    def should_run(self, politician: Dict[str, Any], force: bool = False) -> bool:
        if force:
            return True
        sm = politician.get("social_media") or {}
        smc = politician.get("social_media_citations") or {}
        if not any(v for v in sm.values() if v):
            return True
        for key in _SOCIAL_FIELDS:
            if sm.get(key) and key not in smc:
                return True
        return False

    @log(logger, "PoliticianSocialMedia.run")
    def run(
        self,
        politician: Dict[str, Any],
        force: bool = False,
        context: str = "",
    ) -> Dict[str, Any]:
        if not self.should_run(politician, force):
            return {
                "process": self.name,
                "ok": True,
                "skipped": True,
                "reason": "already_present",
            }

        prompt = PoliticianPrompts.social_media(politician)
        logger.info(
            "social_media: calling LLM (id=%s name=%s)",
            politician.get("id"),
            politician.get("name"),
        )
        raw = self.base._run_llm_with_context(prompt, context)

        parsed = self.base._parse_json_object(raw)
        if parsed is None:
            return {
                "process": self.name,
                "ok": False,
                "error": "invalid_llm_json",
                "raw": raw,
            }

        data = {k: v for k, v in parsed.items() if k != "social_media_citations"}
        smc_raw = parsed.get("social_media_citations") or {}

        adapter = TypeAdapter(SocialMedia)
        validated, errors = self.base._validate_with_adapter(data, adapter)
        if errors:
            return {
                "process": self.name,
                "ok": False,
                "error": "validation_failed",
                "details": errors,
            }
        if validated is None:
            return {
                "process": self.name,
                "ok": False,
                "error": "validation_failed",
            }

        dumped = validated.model_dump(mode="json")
        for key in _SOCIAL_FIELDS:
            if dumped.get(key) and key not in smc_raw:
                return {
                    "process": self.name,
                    "ok": False,
                    "error": "missing_citations",
                    "details": f"social field {key!r} lacks citation",
                }

        updates: Dict[str, Any] = {"social_media": dumped}
        if smc_raw:
            cit_adapter = TypeAdapter(dict[str, Citation])
            smc_val, smc_err = self.base._validate_with_adapter(smc_raw, cit_adapter)
            if smc_err:
                return {
                    "process": self.name,
                    "ok": False,
                    "error": "citation_validation_failed",
                    "details": smc_err,
                }
            if smc_val:
                updates["social_media_citations"] = {
                    k: v.model_dump(mode="json") for k, v in smc_val.items()
                }

        return {"process": self.name, "ok": True, "skipped": False, "updates": updates}


class PoliticianFamilyBackground:
    """Family background enrichment process for one politician."""

    name = "family_background"

    def __init__(self, base_agent: BaseAgent):
        self.base = base_agent

    def should_run(self, politician: Dict[str, Any], force: bool = False) -> bool:
        if force:
            return True
        fam = politician.get("family_background")
        if fam is None:
            return True
        if not fam:
            return False
        return any(not (isinstance(x, dict) and x.get("citation")) for x in fam)

    @log(logger, "PoliticianFamilyBackground.run")
    def run(
        self,
        politician: Dict[str, Any],
        force: bool = False,
        context: str = "",
    ) -> Dict[str, Any]:
        if not self.should_run(politician, force):
            return {
                "process": self.name,
                "ok": True,
                "skipped": True,
                "reason": "already_present",
            }

        prompt = PoliticianPrompts.family_background(politician)
        logger.info(
            "family_background: calling LLM (id=%s name=%s)",
            politician.get("id"),
            politician.get("name"),
        )
        raw = self.base._run_llm_with_context(prompt, context)
        parsed = self.base._parse_json_value(raw)

        if parsed is None:
            return {
                "process": self.name,
                "ok": False,
                "error": "invalid_llm_json",
                "raw": raw,
            }

        items = self.base._coerce_to_list(parsed)
        if items is None:
            return {
                "process": self.name,
                "ok": False,
                "error": "invalid_shape",
                "raw": raw,
            }

        adapter = TypeAdapter(list[FamilyMember])
        validated, errors = self.base._validate_with_adapter(items, adapter)
        if errors:
            return {
                "process": self.name,
                "ok": False,
                "error": "validation_failed",
                "details": errors,
            }

        if validated and any(item.citation is None for item in validated):
            return {
                "process": self.name,
                "ok": False,
                "error": "missing_citations",
            }

        updates = {
            "family_background": [item.model_dump(mode="json") for item in validated]
        }
        return {"process": self.name, "ok": True, "skipped": False, "updates": updates}


class PoliticianCriminalRecords:
    """Criminal records enrichment process for one politician."""

    name = "criminal_records"

    def __init__(self, base_agent: BaseAgent):
        self.base = base_agent

    def should_run(self, politician: Dict[str, Any], force: bool = False) -> bool:
        if force:
            return True
        if has_primary_citations(politician.get("criminal_records")):
            return False
        cr = politician.get("criminal_records")
        if cr is None:
            return True
        if not cr:
            return False
        return any(not (isinstance(x, dict) and x.get("citation")) for x in cr)

    @log(logger, "PoliticianCriminalRecords.run")
    def run(
        self,
        politician: Dict[str, Any],
        force: bool = False,
        context: str = "",
    ) -> Dict[str, Any]:
        if not self.should_run(politician, force):
            return {
                "process": self.name,
                "ok": True,
                "skipped": True,
                "reason": "already_present",
            }

        prompt = PoliticianPrompts.criminal_records(politician)
        logger.info(
            "criminal_records: calling LLM (id=%s name=%s)",
            politician.get("id"),
            politician.get("name"),
        )
        raw = self.base._run_llm_with_context(prompt, context)
        parsed = self.base._parse_json_value(raw)

        if parsed is None:
            return {
                "process": self.name,
                "ok": False,
                "error": "invalid_llm_json",
                "raw": raw,
            }

        items = self.base._coerce_to_list(parsed)
        if items is None:
            return {
                "process": self.name,
                "ok": False,
                "error": "invalid_shape",
                "raw": raw,
            }

        adapter = TypeAdapter(list[CrimeRecord])
        validated, errors = self.base._validate_with_adapter(items, adapter)
        if errors:
            return {
                "process": self.name,
                "ok": False,
                "error": "validation_failed",
                "details": errors,
            }

        if validated and any(item.citation is None for item in validated):
            return {
                "process": self.name,
                "ok": False,
                "error": "missing_citations",
            }

        updates = {
            "criminal_records": [item.model_dump(mode="json") for item in validated]
        }
        return {"process": self.name, "ok": True, "skipped": False, "updates": updates}


class PoliticianContact:
    """Contact information enrichment process for one politician."""

    name = "contact"

    def __init__(self, base_agent: BaseAgent):
        self.base = base_agent

    def should_run(self, politician: Dict[str, Any], force: bool = False) -> bool:
        if force:
            return True
        c = politician.get("contact") or {}
        cc = politician.get("contact_citations") or {}
        if not any(v for v in c.values() if v):
            return True
        for key in _CONTACT_FIELDS:
            if c.get(key) and key not in cc:
                return True
        return False

    @log(logger, "PoliticianContact.run")
    def run(
        self,
        politician: Dict[str, Any],
        force: bool = False,
        context: str = "",
    ) -> Dict[str, Any]:
        if not self.should_run(politician, force):
            return {
                "process": self.name,
                "ok": True,
                "skipped": True,
                "reason": "already_present",
            }

        prompt = PoliticianPrompts.contact(politician)
        logger.info(
            "contact: calling LLM (id=%s name=%s)",
            politician.get("id"),
            politician.get("name"),
        )
        raw = self.base._run_llm_with_context(prompt, context)

        parsed = self.base._parse_json_object(raw)
        if parsed is None:
            return {
                "process": self.name,
                "ok": False,
                "error": "invalid_llm_json",
                "raw": raw,
            }

        data = {k: v for k, v in parsed.items() if k != "contact_citations"}
        cc_raw = parsed.get("contact_citations") or {}

        adapter = TypeAdapter(Contact)
        validated, errors = self.base._validate_with_adapter(data, adapter)
        if errors:
            return {
                "process": self.name,
                "ok": False,
                "error": "validation_failed",
                "details": errors,
            }
        if validated is None:
            return {
                "process": self.name,
                "ok": False,
                "error": "validation_failed",
            }

        dumped = validated.model_dump(mode="json")
        for key in _CONTACT_FIELDS:
            if dumped.get(key) and key not in cc_raw:
                return {
                    "process": self.name,
                    "ok": False,
                    "error": "missing_citations",
                    "details": f"contact field {key!r} lacks citation",
                }

        updates: Dict[str, Any] = {"contact": dumped}
        if cc_raw:
            cit_adapter = TypeAdapter(dict[str, Citation])
            cc_val, cc_err = self.base._validate_with_adapter(cc_raw, cit_adapter)
            if cc_err:
                return {
                    "process": self.name,
                    "ok": False,
                    "error": "citation_validation_failed",
                    "details": cc_err,
                }
            if cc_val:
                updates["contact_citations"] = {
                    k: v.model_dump(mode="json") for k, v in cc_val.items()
                }

        return {"process": self.name, "ok": True, "skipped": False, "updates": updates}


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class PoliticianAgent(BaseAgent):
    """Top-level orchestrator for politician enrichment processes."""

    def __init__(self) -> None:
        super().__init__()
        self.politician_service = PoliticianService()
        self.source_orchestrator = SourceOrchestrator(
            politician_service=self.politician_service
        )
        from app.agents.citation_agent import CitationAgent

        self.citation_agent = CitationAgent()
        self.citation_agent.politician_service = self.politician_service
        self.cache = CacheManager()
        self.processes = [
            PoliticianEducation(self),
            PoliticianPoliticalBackground(self),
            PoliticianSocialMedia(self),
            PoliticianFamilyBackground(self),
            PoliticianCriminalRecords(self),
            PoliticianContact(self),
        ]

    @log(logger, "PoliticianAgent.run")
    def run(
        self,
        politician_id: Optional[str] = None,
        election_type: Optional[Literal["MP", "MLA"]] = None,
        force: bool = False,
        limit: int = 0,
        *,
        source_names: Optional[list[str]] = None,
        skip_sources: bool = False,
        skip_citations: bool = False,
    ) -> Dict[str, Any]:
        """Run source sync, LLM enrichment, and citation backfill for politician(s)."""
        if source_names is None:
            source_names = list(DEFAULT_PIPELINE_SOURCES)

        self.clear_errors()
        pipeline = {
            "source_names": source_names,
            "skip_sources": skip_sources,
            "skip_citations": skip_citations,
        }
        try:
            if politician_id:
                return self._run_one_by_id(politician_id, force=force, **pipeline)
            return self._run_all(
                election_type=election_type, force=force, limit=limit, **pipeline
            )
        finally:
            self.print_error_summary()

    @log(logger, "PoliticianAgent._is_cached")
    def _is_cached(self, politician_id: str) -> bool:
        return self.cache.exists(politician_id)

    @log(logger, "PoliticianAgent._mark_cached")
    def _mark_cached(self, politician_id: str) -> None:
        self.cache.set(politician_id, {"processed": True})

    def _process_cache_key(self, politician_id: str, process_name: str) -> str:
        return f"{politician_id}:{process_name}"

    def _is_process_cached(self, politician_id: str, process_name: str) -> bool:
        return self.cache.exists(self._process_cache_key(politician_id, process_name))

    def _mark_process_cached(self, politician_id: str, process_name: str) -> None:
        self.cache.set(
            self._process_cache_key(politician_id, process_name), {"processed": True}
        )

    @log(logger, "PoliticianAgent._run_one_by_id")
    def _run_one_by_id(
        self,
        politician_id: str,
        force: bool = False,
        *,
        source_names: Optional[list[str]] = None,
        skip_sources: bool = False,
        skip_citations: bool = False,
    ) -> Dict[str, Any]:
        politician = self.politician_service.get_by_id(politician_id)
        if not politician:
            return {"ok": False, "id": politician_id, "error": "politician_not_found"}

        return self._run_for_politician(
            politician,
            force=force,
            source_names=source_names,
            skip_sources=skip_sources,
            skip_citations=skip_citations,
        )

    @log(logger, "PoliticianAgent._run_all")
    def _run_all(
        self,
        election_type: Optional[Literal["MP", "MLA"]] = None,
        force: bool = False,
        limit: int = 0,
        *,
        source_names: Optional[list[str]] = None,
        skip_sources: bool = False,
        skip_citations: bool = False,
    ) -> Dict[str, Any]:
        if election_type in ("MP", "MLA"):
            politicians = self.politician_service.get_all(election_type)
        else:
            politicians = self.politician_service.get_all_politicians()

        if limit and limit > 0:
            politicians = politicians[:limit]

        summary: Dict[str, Any] = {
            "total": len(politicians),
            "processed": 0,
            "skipped": 0,
            "failed": 0,
        }

        for idx, politician in enumerate(politicians, 1):
            pid = politician.get("id")
            if not pid:
                summary["failed"] += 1
                continue

            # ── Fast-path: skip fully-cached politicians ─────────────────
            if not force and self._is_cached(pid):
                needs_work = any(
                    p.should_run(politician, force) for p in self.processes
                )
                if not needs_work:
                    logger.info(
                        "[%d/%d] SKIP %s (%s) — fully enriched",
                        idx,
                        len(politicians),
                        politician.get("name"),
                        pid,
                    )
                    summary["skipped"] += 1
                    continue

            logger.info(
                "[%d/%d] politician=%s name=%s",
                idx,
                len(politicians),
                pid,
                politician.get("name"),
            )

            result = self._run_for_politician(
                politician,
                force=force,
                source_names=source_names,
                skip_sources=skip_sources,
                skip_citations=skip_citations,
            )
            if result.get("ok"):
                summary["processed"] += 1
            else:
                summary["failed"] += 1

        logger.info(
            "Run complete: %d total, %d processed, %d skipped, %d failed",
            summary["total"],
            summary["processed"],
            summary["skipped"],
            summary["failed"],
        )
        return summary

    @log(logger, "PoliticianAgent._run_for_politician")
    def _run_for_politician(
        self,
        politician: Dict[str, Any],
        force: bool = False,
        *,
        source_names: Optional[list[str]] = None,
        skip_sources: bool = False,
        skip_citations: bool = False,
    ) -> Dict[str, Any]:
        """Run source sync, LLM enrichment, and citation backfill for one politician."""
        politician_id = politician.get("id")
        if not politician_id:
            return {"ok": False, "error": "missing_politician_id"}

        if source_names is None:
            source_names = list(DEFAULT_PIPELINE_SOURCES)

        process_results: list[Dict[str, Any]] = []
        updated_fields: set[str] = set()

        def _append_skipped(process_name: str, reason: str) -> None:
            process_results.append(
                {
                    "process": process_name,
                    "ok": True,
                    "skipped": True,
                    "reason": reason,
                }
            )

        if not skip_sources and source_names:
            logger.info(
                "Source sync for %s (%s): sources=%s",
                politician.get("name"),
                politician_id,
                source_names,
            )
            try:
                sync_result = self.source_orchestrator.sync_politician(
                    politician,
                    source_names=source_names,
                    force=force,
                )
                process_results.append(
                    {
                        "process": "source_sync",
                        "ok": bool(sync_result.get("ok")),
                        "skipped": not sync_result.get("sources_run"),
                        "sources_run": sync_result.get("sources_run", []),
                        "errors": sync_result.get("errors", []),
                        "issues": sync_result.get("issues", []),
                    }
                )
            except Exception as exc:
                logger.warning(
                    "Source sync failed for %s: %s",
                    politician_id,
                    exc,
                )
                self._record_error(
                    "source_sync",
                    str(exc),
                    context=str(politician_id),
                    exc=exc,
                )
                process_results.append(
                    {
                        "process": "source_sync",
                        "ok": False,
                        "error": str(exc),
                    }
                )

            fresh = self.politician_service.get_by_id(str(politician_id))
            if fresh:
                politician = fresh

        needing: list[str] = []
        for process in self.processes:
            if not force and self._is_process_cached(str(politician_id), process.name):
                continue
            if process.should_run(politician, force):
                needing.append(process.name)

        if needing:
            logger.info(
                "Sequential enrichment for %s (%s); processes: %s",
                politician.get("name"),
                politician_id,
                needing,
            )

            context = self._gather_politician_context(politician)
            if context:
                logger.info(
                    "Context gathered (%d chars) for %s",
                    len(context),
                    politician.get("name"),
                )
            else:
                logger.info(
                    "No external context for %s — LLM knowledge only",
                    politician.get("name"),
                )

            for process in self.processes:
                pname = process.name

                if not force and self._is_process_cached(str(politician_id), pname):
                    _append_skipped(pname, "cached_processed")
                    continue
                if not process.should_run(politician, force):
                    _append_skipped(pname, "already_present")
                    continue

                logger.info(
                    "PoliticianAgent START process=%s id=%s name=%s",
                    pname,
                    politician_id,
                    politician.get("name"),
                )
                try:
                    result = process.run(politician, force, context)
                except Exception as exc:
                    if _is_llm_quota_exc(exc):
                        logger.error(
                            "Process %s hit LLM quota for %s: %s",
                            pname,
                            politician_id,
                            exc,
                        )
                        raise
                    logger.error(
                        "Process %s crashed for %s: %s",
                        pname,
                        politician_id,
                        exc,
                    )
                    self._record_error(
                        "agent",
                        f"Process {pname} crashed: {exc}",
                        context=str(politician_id),
                        exc=exc,
                    )
                    process_results.append(
                        {"process": pname, "ok": False, "error": str(exc)}
                    )
                    continue

                process_results.append(result)

                if result.get("ok") and not result.get("skipped"):
                    self._mark_process_cached(str(politician_id), pname)

                update_keys = (
                    list(result["updates"].keys())
                    if result.get("ok")
                    and not result.get("skipped")
                    and result.get("updates")
                    else []
                )

                if update_keys:
                    updated = self.politician_service.update_politician(
                        str(politician_id), result["updates"]
                    )
                    if not updated:
                        process_results.append(
                            {"process": pname, "ok": False, "error": "update_failed"}
                        )
                    else:
                        for k in result["updates"]:
                            updated_fields.add(k)
                        fresh = self.politician_service.get_by_id(str(politician_id))
                        if fresh:
                            politician = fresh
        else:
            for process in self.processes:
                if not force and self._is_process_cached(
                    str(politician_id), process.name
                ):
                    _append_skipped(process.name, "cached_processed")
                elif not process.should_run(politician, force):
                    _append_skipped(process.name, "already_present")
                else:
                    _append_skipped(process.name, "cached_processed")

            logger.info(
                "All LLM fields present for %s (%s) — skipping enrichment processes",
                politician.get("name"),
                politician_id,
            )
            self._mark_cached(str(politician_id))

        if not skip_citations:
            logger.info(
                "Citation backfill for %s (%s)",
                politician.get("name"),
                politician_id,
            )
            try:
                cite_result = self.citation_agent._run_for_politician(
                    politician, force=force
                )
                process_results.append(
                    {"process": "citation_backfill", **cite_result}
                )
                if cite_result.get("updated_fields"):
                    updated_fields.update(cite_result["updated_fields"])
                fresh = self.politician_service.get_by_id(str(politician_id))
                if fresh:
                    politician = fresh
            except Exception as exc:
                if _is_llm_quota_exc(exc):
                    raise
                logger.warning(
                    "Citation backfill failed for %s: %s",
                    politician_id,
                    exc,
                )
                self._record_error(
                    "citation",
                    str(exc),
                    context=str(politician_id),
                    exc=exc,
                )
                process_results.append(
                    {
                        "process": "citation_backfill",
                        "ok": False,
                        "error": str(exc),
                    }
                )

        if needing:
            self._mark_cached(str(politician_id))

        has_error = any(not r.get("ok") for r in process_results)
        return {
            "ok": not has_error,
            "id": politician_id,
            "updated_fields": sorted(updated_fields),
            "process_results": process_results,
        }
