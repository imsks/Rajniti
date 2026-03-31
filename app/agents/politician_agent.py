from __future__ import annotations

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Literal, Optional

from pydantic import TypeAdapter

from app.agents.base_agent import BaseAgent
from app.core import CacheManager, log
from app.prompts import PoliticianPrompts
from app.schemas.politician import (
    Contact,
    CrimeRecord,
    Education,
    ElectionRecord,
    FamilyMember,
    PoliticalBackground,
    SocialMedia,
)
from app.services import PoliticianService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sub-processes (each enriches one field)
# ---------------------------------------------------------------------------


class PoliticianEducation:
    """Education enrichment process for one politician."""

    name = "education"

    def __init__(self, base_agent: BaseAgent):
        self.base = base_agent

    def should_run(self, politician: Dict[str, Any], force: bool = False) -> bool:
        return force or not politician.get("education")

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
        elections = (politician.get("political_background") or {}).get(
            "elections"
        ) or []
        return not elections

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

        pb["elections"] = [e.model_dump(mode="json") for e in ev_validated]
        updates["political_background"] = pb
        logger.info(
            "political_background: elections-only prompt filled %d records (id=%s)",
            len(pb["elections"]),
            politician.get("id"),
        )


class PoliticianSocialMedia:
    """Social media enrichment process for one politician."""

    name = "social_media"

    def __init__(self, base_agent: BaseAgent):
        self.base = base_agent

    def should_run(self, politician: Dict[str, Any], force: bool = False) -> bool:
        if force:
            return True
        existing = politician.get("social_media") or {}
        return not any(v for v in existing.values() if v)

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

        adapter = TypeAdapter(SocialMedia)
        validated, errors = self.base._validate_with_adapter(parsed, adapter)
        if errors:
            return {
                "process": self.name,
                "ok": False,
                "error": "validation_failed",
                "details": errors,
            }

        updates = {"social_media": validated.model_dump(mode="json")}
        return {"process": self.name, "ok": True, "skipped": False, "updates": updates}


class PoliticianFamilyBackground:
    """Family background enrichment process for one politician."""

    name = "family_background"

    def __init__(self, base_agent: BaseAgent):
        self.base = base_agent

    def should_run(self, politician: Dict[str, Any], force: bool = False) -> bool:
        return force or not politician.get("family_background")

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
        return force or not politician.get("criminal_records")

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
        existing = politician.get("contact") or {}
        return not any(v for v in existing.values() if v)

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

        adapter = TypeAdapter(Contact)
        validated, errors = self.base._validate_with_adapter(parsed, adapter)
        if errors:
            return {
                "process": self.name,
                "ok": False,
                "error": "validation_failed",
                "details": errors,
            }

        updates = {"contact": validated.model_dump(mode="json")}
        return {"process": self.name, "ok": True, "skipped": False, "updates": updates}


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class PoliticianAgent(BaseAgent):
    """Top-level orchestrator for politician enrichment processes."""

    def __init__(self) -> None:
        super().__init__()
        self.politician_service = PoliticianService()
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
    ) -> Dict[str, Any]:
        """Run enrichment for one politician or all politicians by type."""
        self.clear_errors()
        try:
            if politician_id:
                return self._run_one_by_id(politician_id, force=force)
            return self._run_all(election_type=election_type, force=force, limit=limit)
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
    def _run_one_by_id(self, politician_id: str, force: bool = False) -> Dict[str, Any]:
        politician = self.politician_service.get_by_id(politician_id)
        if not politician:
            return {"ok": False, "id": politician_id, "error": "politician_not_found"}

        return self._run_for_politician(politician, force=force)

    @log(logger, "PoliticianAgent._run_all")
    def _run_all(
        self,
        election_type: Optional[Literal["MP", "MLA"]] = None,
        force: bool = False,
        limit: int = 0,
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

            result = self._run_for_politician(politician, force=force)
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
        self, politician: Dict[str, Any], force: bool = False
    ) -> Dict[str, Any]:
        """Pre-check what needs work, gather context only if necessary,
        then run only the active sub-processes in parallel."""
        politician_id = politician.get("id")
        if not politician_id:
            return {"ok": False, "error": "missing_politician_id"}

        # ── 1. Pre-check: which processes actually need to run? ──────────
        active_processes: list = []
        skipped_results: list[Dict[str, Any]] = []

        for process in self.processes:
            if not force and self._is_process_cached(politician_id, process.name):
                skipped_results.append(
                    {
                        "process": process.name,
                        "ok": True,
                        "skipped": True,
                        "reason": "cached_processed",
                    }
                )
                continue
            if process.should_run(politician, force):
                active_processes.append(process)
            else:
                skipped_results.append(
                    {
                        "process": process.name,
                        "ok": True,
                        "skipped": True,
                        "reason": "already_present",
                    }
                )

        if not active_processes:
            logger.info(
                "All data present for %s (%s) — nothing to enrich",
                politician.get("name"),
                politician_id,
            )
            self._mark_cached(politician_id)
            return {
                "ok": True,
                "id": politician_id,
                "updated_fields": [],
                "process_results": skipped_results,
            }

        logger.info(
            "%d/%d processes need data for %s: %s",
            len(active_processes),
            len(self.processes),
            politician.get("name"),
            [p.name for p in active_processes],
        )

        # ── 2. Gather real-world context ONLY when there is work to do ───
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

        # ── 3. Run only active processes in parallel ─────────────────────
        process_results: list[Dict[str, Any]] = list(skipped_results)
        updated_fields: set[str] = set()
        write_lock = threading.Lock()

        with ThreadPoolExecutor(max_workers=max(1, len(active_processes))) as executor:
            future_to_process = {
                executor.submit(process.run, politician, force, context): process
                for process in active_processes
            }
            for future in as_completed(future_to_process):
                process = future_to_process[future]
                try:
                    result = future.result()
                except Exception as exc:
                    pname = getattr(process, "name", str(process))
                    logger.error(
                        "Process %s crashed for %s: %s",
                        pname,
                        politician_id,
                        exc,
                    )
                    self._record_error(
                        "agent",
                        f"Process {pname} crashed: {exc}",
                        context=politician_id,
                        exc=exc,
                    )
                    process_results.append(
                        {"process": pname, "ok": False, "error": str(exc)}
                    )
                    continue

                process_results.append(result)

                # ── 4. Persist updates immediately (serialised) ──────────
                if result.get("ok") and not result.get("skipped"):
                    self._mark_process_cached(politician_id, process.name)
                if (
                    result.get("ok")
                    and not result.get("skipped")
                    and result.get("updates")
                ):
                    with write_lock:
                        updated = self.politician_service.update_politician(
                            politician_id, result["updates"]
                        )
                        if not updated:
                            logger.error(
                                "Failed to persist updates for %s from process %s",
                                politician_id,
                                getattr(process, "name", "unknown"),
                            )
                            process_results.append(
                                {
                                    "process": getattr(process, "name", "unknown"),
                                    "ok": False,
                                    "error": "update_failed",
                                }
                            )
                        else:
                            for k in result["updates"]:
                                updated_fields.add(k)
                            logger.info(
                                "Persisted %s for %s from %s",
                                list(result["updates"].keys()),
                                politician_id,
                                getattr(process, "name", "unknown"),
                            )

        # ── 5. Mark cached and return ────────────────────────────────────
        self._mark_cached(politician_id)

        has_error = any(not r.get("ok") for r in process_results)
        return {
            "ok": not has_error,
            "id": politician_id,
            "updated_fields": sorted(updated_fields),
            "process_results": process_results,
        }
