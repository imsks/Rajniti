"""Citation backfill agent: only adds missing source URLs to existing detail fields."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Literal, Optional

from pydantic import TypeAdapter

from app.agents.base_agent import BaseAgent
from app.agents.citation_audit_merge import (
    CITATION_COVERAGE_SKIP_THRESHOLD_PCT,
    merge_citation_audit_updates,
    politician_citation_coverage_pct,
    politician_citation_gaps,
    politician_needs_citation_audit,
)
from app.agents.politician_agent import _is_llm_quota_exc
from app.core import CacheManager, log
from app.prompts import PoliticianPrompts
from app.schemas.politician import CitationAuditLLMResult
from app.services import PoliticianService

logger = logging.getLogger(__name__)

PROCESS_NAME = "citation_backfill"


class CitationAgent(BaseAgent):
    """Runs citation-only LLM pass for rows that still lack source links."""

    def __init__(self) -> None:
        super().__init__()
        self.politician_service = PoliticianService()
        self.cache = CacheManager()

    def _process_cache_key(self, politician_id: str) -> str:
        return f"{politician_id}:{PROCESS_NAME}"

    def _mark_process_cached(self, politician_id: str) -> None:
        self.cache.set(self._process_cache_key(politician_id), {"processed": True})

    @log(logger, "CitationAgent.run")
    def run(
        self,
        politician_id: Optional[str] = None,
        election_type: Optional[Literal["MP", "MLA"]] = None,
        force: bool = False,
        limit: int = 0,
    ) -> Dict[str, Any]:
        self.clear_errors()
        try:
            if politician_id:
                return self._run_one_by_id(politician_id, force=force)
            return self._run_all(election_type=election_type, force=force, limit=limit)
        finally:
            self.print_error_summary()

    @log(logger, "CitationAgent._run_one_by_id")
    def _run_one_by_id(self, politician_id: str, force: bool = False) -> Dict[str, Any]:
        politician = self.politician_service.get_by_id(politician_id)
        if not politician:
            return {"ok": False, "id": politician_id, "error": "politician_not_found"}
        return self._run_for_politician(politician, force=force)

    @log(logger, "CitationAgent._run_all")
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

            if not force:
                cov = politician_citation_coverage_pct(politician)
                if cov is None or cov >= CITATION_COVERAGE_SKIP_THRESHOLD_PCT:
                    summary["skipped"] += 1
                    continue
                if politician_citation_gaps(politician) is None:
                    summary["skipped"] += 1
                    continue

            logger.info(
                "CitationAgent [%d/%d] id=%s name=%s",
                idx,
                len(politicians),
                pid,
                politician.get("name"),
            )

            result = self._run_for_politician(politician, force=force)
            if not result.get("ok"):
                summary["failed"] += 1
            elif result.get("skipped"):
                summary["skipped"] += 1
            else:
                summary["processed"] += 1

        logger.info(
            "CitationAgent done: total=%d processed=%d skipped=%d failed=%d",
            summary["total"],
            summary["processed"],
            summary["skipped"],
            summary["failed"],
        )
        return summary

    @log(logger, "CitationAgent._run_for_politician")
    def _run_for_politician(
        self,
        politician: Dict[str, Any],
        force: bool = False,
        reraise_llm_quota: bool = False,
    ) -> Dict[str, Any]:
        politician_id = politician.get("id")
        if not politician_id:
            return {"ok": False, "error": "missing_politician_id"}

        pid = str(politician_id)

        cov_pct = politician_citation_coverage_pct(politician)
        backlog = politician_citation_gaps(politician)

        if not force:
            if cov_pct is None:
                return {
                    "ok": True,
                    "id": pid,
                    "skipped": True,
                    "reason": "no_citation_slots",
                }
            if cov_pct >= CITATION_COVERAGE_SKIP_THRESHOLD_PCT:
                return {
                    "ok": True,
                    "id": pid,
                    "skipped": True,
                    "reason": "citation_coverage_at_or_above_threshold",
                    "coverage_pct": cov_pct,
                }
            if backlog is None:
                return {
                    "ok": True,
                    "id": pid,
                    "skipped": True,
                    "reason": "citations_complete",
                    "coverage_pct": cov_pct,
                }

        logger.info(
            "CitationAgent: gathering context for %s (%s)",
            politician.get("name"),
            pid,
        )
        logger.info(
            "CitationAgent: backlog keys=%s coverage_pct=%s",
            sorted(backlog.keys()) if backlog else "(force / none)",
            cov_pct if cov_pct is not None else "n/a",
        )
        context = self._gather_politician_context(politician)
        logger.info(
            "CitationAgent: context length=%d chars for %s",
            len(context),
            politician.get("name"),
        )

        prompt = PoliticianPrompts.citation_audit(politician, citation_backlog=backlog)
        logger.info(
            "CitationAgent: LLM backfill START id=%s name=%s",
            pid,
            politician.get("name"),
        )
        try:
            raw = self._run_llm_with_context(prompt, context)
        except Exception as exc:
            if reraise_llm_quota and _is_llm_quota_exc(exc):
                logger.warning("CitationAgent: LLM quota/limit id=%s err=%s", pid, exc)
                raise
            logger.exception("CitationAgent: LLM failed id=%s err=%s", pid, exc)
            return {"ok": False, "id": pid, "error": str(exc)}

        parsed = self._parse_json_object(raw)
        if parsed is None:
            logger.error(
                "CitationAgent: invalid JSON from LLM id=%s — full raw response (%d chars):\n%s",
                pid,
                len(raw),
                raw,
            )
            return {"ok": False, "id": pid, "error": "invalid_llm_json"}

        adapter = TypeAdapter(CitationAuditLLMResult)
        validated, errors = self._validate_with_adapter(parsed, adapter)
        if errors or validated is None:
            try:
                parsed_sample = json.dumps(
                    parsed, indent=2, ensure_ascii=False, default=str
                )
            except Exception:
                parsed_sample = repr(parsed)
            logger.error(
                "CitationAgent: schema validation failed id=%s errors=%s\n"
                "--- parsed JSON (%d chars) ---\n%s\n"
                "--- raw LLM text (%d chars) ---\n%s",
                pid,
                errors,
                len(parsed_sample),
                parsed_sample,
                len(raw),
                raw,
            )
            return {
                "ok": False,
                "id": pid,
                "error": "validation_failed",
                "details": errors,
            }

        updates, issues = merge_citation_audit_updates(politician, validated)

        if not updates:
            mb = politician_citation_gaps(politician)
            logger.info(
                "CitationAgent: no citation patches produced id=%s issues=%s backlog=%s — "
                "merge only fills EMPTY slots (null LLM proposals or already-cited indices).",
                pid,
                issues,
                mb,
            )
            return {
                "ok": True,
                "id": pid,
                "skipped": True,
                "reason": "no_updates_from_llm",
            }

        logger.info(
            "CitationAgent: persisting keys=%s id=%s",
            list(updates.keys()),
            pid,
        )
        if not self.politician_service.update_politician(pid, updates):
            logger.error("CitationAgent: persist failed id=%s", pid)
            return {"ok": False, "id": pid, "error": "update_failed"}

        recheck = self.politician_service.get_by_id(pid)
        if recheck and not politician_needs_citation_audit(recheck):
            self._mark_process_cached(pid)
            logger.info(
                "CitationAgent: DONE id=%s — fully cited, process cached",
                pid,
            )
        else:
            logger.warning(
                "CitationAgent: DONE id=%s — still missing some citations (not caching)",
                pid,
            )

        return {
            "ok": True,
            "id": pid,
            "updated_fields": sorted(updates.keys()),
            "issues": issues,
        }
