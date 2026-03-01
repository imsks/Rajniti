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


class PoliticianEducation:
    """Education enrichment process for one politician."""

    name = "education"

    def __init__(self, base_agent: BaseAgent):
        """Store shared agent utilities (LLM, parsers, validation helpers)."""
        self.base = base_agent

    @log(logger, "PoliticianEducation.run")
    def run(self, politician: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        """Run education extraction and return a process result payload."""
        if politician.get("education") and not force:
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
        raw = self.base._run_llm(prompt)
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

    @log(logger, "PoliticianPoliticalBackground.run")
    def run(self, politician: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        # skip if present and not force
        existing = (politician.get("political_background") or {}).get("elections") or []
        if existing and not force:
            return {
                "process": self.name,
                "ok": True,
                "skipped": True,
                "reason": "already_present",
            }

        prompt = PoliticianPrompts.political_background(politician)
        raw = self.base._run_llm(prompt)
        parsed = self.base._parse_json_object(raw)
        if parsed is None:
            return {
                "process": self.name,
                "ok": False,
                "error": "invalid_llm_json",
                "raw": raw,
            }
        # Try full validation first
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
            # If elections empty, attempt to fill via focused elections-only prompt
            if not updates["political_background"].get("elections"):
                self._maybe_fill_elections_only(politician, updates)
            return {
                "process": self.name,
                "ok": True,
                "skipped": False,
                "updates": updates,
            }

        # Full validation failed — attempt tolerant partial acceptance:
        validation_errors = errors
        partial_updates: Dict[str, Any] = {"elections": [], "summary": None}

        # Try to validate elections list individually
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
                    "political_background: elections validation failed: %s", ev_errors
                )
        # Accept summary if present and non-empty
        summary_val = parsed.get("summary")
        if isinstance(summary_val, str) and summary_val.strip():
            partial_updates["summary"] = summary_val.strip()

        # If we have at least one useful field, accept partial update (and try to fill elections)
        if partial_updates["elections"] or partial_updates["summary"] is not None:
            updates["political_background"] = partial_updates
            logger.info(
                "political_background: partial acceptance (id=%s) errors=%s",
                politician.get("id"),
                validation_errors,
            )
            self._maybe_fill_elections_only(politician, updates)
            logger.debug("political_background: partial updates=%s", updates)
            return {
                "process": self.name,
                "ok": True,
                "skipped": False,
                "updates": updates,
                "validation_errors": validation_errors,
            }

        # Nothing useful could be extracted
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
        self, politician: Dict[str, Any], updates: Dict[str, Any]
    ) -> None:
        """If elections are empty, issue a focused elections-only prompt and merge."""
        pb = updates.get("political_background") or {}
        if pb.get("elections"):
            return  # already have data

        logger.info(
            "political_background: elections empty; issuing elections-only prompt (id=%s)",
            politician.get("id"),
        )
        prompt = PoliticianPrompts.political_background_elections_only(politician)
        raw = self.base._run_llm(prompt)
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

    @log(logger, "PoliticianSocialMedia.run")
    def run(self, politician: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        existing = politician.get("social_media") or {}
        has_data = any(v for v in existing.values() if v)
        if has_data and not force:
            return {"process": self.name, "ok": True, "skipped": True, "reason": "already_present"}

        prompt = PoliticianPrompts.social_media(politician)
        logger.info("social_media: calling LLM (id=%s name=%s)", politician.get("id"), politician.get("name"))
        raw = self.base._run_llm(prompt)

        parsed = self.base._parse_json_object(raw)
        if parsed is None:
            return {"process": self.name, "ok": False, "error": "invalid_llm_json", "raw": raw}

        adapter = TypeAdapter(SocialMedia)
        validated, errors = self.base._validate_with_adapter(parsed, adapter)
        if errors:
            return {"process": self.name, "ok": False, "error": "validation_failed", "details": errors}

        updates = {"social_media": validated.model_dump(mode="json")}
        return {"process": self.name, "ok": True, "skipped": False, "updates": updates}


class PoliticianFamilyBackground:
    """Family background enrichment process for one politician."""

    name = "family_background"

    def __init__(self, base_agent: BaseAgent):
        self.base = base_agent

    @log(logger, "PoliticianFamilyBackground.run")
    def run(self, politician: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        if politician.get("family_background") and not force:
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
        raw = self.base._run_llm(prompt)
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

    @log(logger, "PoliticianCriminalRecords.run")
    def run(self, politician: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        if politician.get("criminal_records") and not force:
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
        raw = self.base._run_llm(prompt)
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

    @log(logger, "PoliticianContact.run")
    def run(self, politician: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        existing = politician.get("contact") or {}
        has_data = any(v for v in existing.values() if v)
        if has_data and not force:
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
        raw = self.base._run_llm(prompt)

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


class PoliticianAgent(BaseAgent):
    """Top-level orchestrator for politician enrichment processes."""

    def __init__(self):
        """Initialize dependencies and register available processes."""
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
        if politician_id:
            return self._run_one_by_id(politician_id, force=force)
        return self._run_all(election_type=election_type, force=force, limit=limit)

    @log(logger, "PoliticianAgent._is_cached")
    def _is_cached(self, politician_id: str) -> bool:
        """Return True when politician id already exists in cache."""
        return self.cache.exists(politician_id)

    @log(logger, "PoliticianAgent._mark_cached")
    def _mark_cached(self, politician_id: str) -> None:
        """Mark politician id as processed (full/partial both count)."""
        self.cache.set(politician_id, {"processed": True})

    @log(logger, "PoliticianAgent._run_one_by_id")
    def _run_one_by_id(self, politician_id: str, force: bool = False) -> Dict[str, Any]:
        """Run all processes for a single politician id.

        Each subprocess decides independently whether to fetch or skip
        based on whether its field already has data.
        """
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
        """Run all processes for MP/MLA/all politicians."""
        if election_type in ("MP", "MLA"):
            politicians = self.politician_service.get_all(election_type)
        else:
            politicians = self.politician_service.get_all_politicians()

        if limit and limit > 0:
            politicians = politicians[:limit]

        summary = {"total": len(politicians), "processed": 0, "failed": 0}
        for idx, politician in enumerate(politicians, 1):
            pid = politician.get("id")
            if not pid:
                summary["failed"] += 1
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

        return summary

    @log(logger, "PoliticianAgent._run_for_politician")
    def _run_for_politician(
        self, politician: Dict[str, Any], force: bool = False
    ) -> Dict[str, Any]:
        """Run registered processes in parallel for one politician."""
        politician_id = politician.get("id")
        if not politician_id:
            return {"ok": False, "error": "missing_politician_id"}

        process_results: list[Dict[str, Any]] = []
        updated_fields: set[str] = set()

        # Per-politician write lock to serialize file writes from concurrent processes
        write_lock = threading.Lock()

        with ThreadPoolExecutor(max_workers=max(1, len(self.processes))) as executor:
            future_to_process = {
                executor.submit(process.run, politician, force): process
                for process in self.processes
            }
            for future in as_completed(future_to_process):
                process = future_to_process[future]
                try:
                    result = future.result()
                except Exception as exc:
                    logger.exception(
                        "process %s crashed: %s",
                        getattr(process, "name", str(process)),
                        exc,
                    )
                    # record failure for summary
                    process_results.append(
                        {
                            "process": getattr(process, "name", "unknown"),
                            "ok": False,
                            "error": str(exc),
                        }
                    )
                    continue

                process_results.append(result)

                # Persist each process's updates immediately (serialized by write_lock)
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
                            # track updated fields for reporting
                            for k in result["updates"].keys():
                                updated_fields.add(k)
                            logger.info(
                                "Persisted updates for %s from process %s: %s",
                                politician_id,
                                getattr(process, "name", "unknown"),
                                list(result["updates"].keys()),
                            )

        self._mark_cached(politician_id)

        has_error = any(not r.get("ok") for r in process_results)
        return {
            "ok": not has_error,
            "id": politician_id,
            "updated_fields": sorted(list(updated_fields)),
            "process_results": process_results,
        }
