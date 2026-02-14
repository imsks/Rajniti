from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Literal, Optional

from pydantic import TypeAdapter

from app.agents.base_agent import BaseAgent
from app.core import CacheManager, log
from app.services import PoliticianService
from app.schemas.politician import Education

logger = logging.getLogger(__name__)


class PoliticianEducation:
    """Education enrichment process for one politician."""

    name = "education"

    def __init__(self, base_agent: BaseAgent):
        """Store shared agent utilities (LLM, parsers, validation helpers)."""
        self.base = base_agent

    def _build_prompt(self, politician: Dict[str, Any]) -> str:
        """Build a strict JSON prompt for education extraction."""
        name = politician.get("name", "")
        state = politician.get("state", "")
        constituency = politician.get("constituency", "")
        ptype = politician.get("type", "")

        return (
            "You are extracting structured data about an Indian politician.\n"
            "Return ONLY valid JSON array. Each item format:\n"
            "[{\"qualification\": \"HIGH_SCHOOL|DIPLOMA|BACHELOR|MASTER|DOCTORATE|PROFESSIONAL|OTHERS|null\", "
            "\"institution\": \"string|null\", \"year_completed\": number|null}]\n"
            f"Politician: {name}\nType: {ptype}\nState: {state}\nConstituency: {constituency}\n"
            "If unknown, return []"
        )

    @log(logger, "PoliticianEducation.run")
    def run(self, politician: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        """Run education extraction and return a process result payload."""
        if politician.get("education") and not force:
            return {"process": self.name, "ok": True, "skipped": True, "reason": "already_present"}

        prompt = self._build_prompt(politician)
        logger.info("education: calling LLM (id=%s name=%s)", politician.get("id"), politician.get("name"))
        raw = self.base._run_llm(prompt)
        parsed = self.base._parse_json_value(raw)

        if parsed is None:
            return {"process": self.name, "ok": False, "error": "invalid_llm_json", "raw": raw}

        items = self.base._coerce_to_list(parsed)
        if items is None:
            return {"process": self.name, "ok": False, "error": "invalid_shape", "raw": raw}

        adapter = TypeAdapter(list[Education])
        validated, errors = self.base._validate_with_adapter(items, adapter)
        if errors:
            return {"process": self.name, "ok": False, "error": "validation_failed", "details": errors}

        updates = {"education": [item.model_dump(mode="json") for item in validated]}
        return {"process": self.name, "ok": True, "skipped": False, "updates": updates}


class PoliticianAgent(BaseAgent):
    """Top-level orchestrator for politician enrichment processes."""

    def __init__(self):
        """Initialize dependencies and register available processes."""
        super().__init__()
        self.politician_service = PoliticianService()
        self.cache = CacheManager()
        self.processes = [PoliticianEducation(self)]

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
        """Run all processes for a single politician id."""
        if self._is_cached(politician_id) and not force:
            logger.info("skip cached: %s", politician_id)
            return {"ok": True, "id": politician_id, "skipped": True, "reason": "already_processed"}

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

        summary = {"total": len(politicians), "processed": 0, "skipped": 0, "failed": 0}
        for idx, politician in enumerate(politicians, 1):
            pid = politician.get("id")
            if not pid:
                summary["failed"] += 1
                continue

            logger.info("[%d/%d] politician=%s name=%s", idx, len(politicians), pid, politician.get("name"))

            if self._is_cached(pid) and not force:
                summary["skipped"] += 1
                logger.info("  ↳ skipped (cached)")
                continue

            result = self._run_for_politician(politician, force=force)
            if result.get("ok"):
                summary["processed"] += 1
            else:
                summary["failed"] += 1

        return summary

    @log(logger, "PoliticianAgent._run_for_politician")
    def _run_for_politician(self, politician: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        """Run registered processes in parallel for one politician."""
        politician_id = politician.get("id")
        if not politician_id:
            return {"ok": False, "error": "missing_politician_id"}

        process_results: list[Dict[str, Any]] = []
        updates: Dict[str, Any] = {}

        with ThreadPoolExecutor(max_workers=max(1, len(self.processes))) as executor:
            futures = [executor.submit(process.run, politician, force) for process in self.processes]
            for future in as_completed(futures):
                result = future.result()
                process_results.append(result)
                if result.get("ok") and not result.get("skipped") and result.get("updates"):
                    updates.update(result["updates"])

        if updates:
            updated = self.politician_service.update_politician(politician_id, updates)
            if not updated:
                return {
                    "ok": False,
                    "id": politician_id,
                    "error": "update_failed",
                    "process_results": process_results,
                }

        # Per requirement: if id is processed once (even partial), skip in future.
        self._mark_cached(politician_id)

        has_error = any(not r.get("ok") for r in process_results)
        return {
            "ok": not has_error,
            "id": politician_id,
            "updated_fields": sorted(list(updates.keys())),
            "process_results": process_results,
        }
