"""Orchestrate source fetch → merge → persist for one politician."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.services import PoliticianService
from app.sources.merge import merge_source_results
from app.sources.registry import list_sources

logger = logging.getLogger(__name__)


class SourceOrchestrator:
    """Run registered sources for politicians and persist merged updates."""

    def __init__(
        self,
        politician_service: Optional[PoliticianService] = None,
    ) -> None:
        self.politician_service = politician_service or PoliticianService()

    def sync_politician(
        self,
        politician: Dict[str, Any],
        *,
        source_names: Optional[List[str]] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        pid = politician.get("id")
        if not pid:
            raise ValueError("Politician missing id")

        modules = list_sources(names=source_names)
        results = []
        errors: List[str] = []

        for mod in modules:
            if not mod.can_fetch(politician, force=force):
                logger.debug("Skip source %s for %s", mod.NAME, pid)
                continue
            try:
                result = mod.fetch(politician, force=force)
                results.append(result)
                politician = merge_source_results(politician, [result])
            except Exception as exc:
                msg = f"{mod.NAME}: {exc}"
                logger.warning("Source fetch failed for %s: %s", pid, msg)
                errors.append(msg)

        if not results:
            return {
                "id": pid,
                "ok": False,
                "sources_run": [],
                "errors": errors or ["no sources ran"],
            }

        merged = merge_source_results(politician, results)

        self.politician_service.update_politician(str(pid), merged)

        return {
            "id": pid,
            "ok": True,
            "sources_run": [r.source_name for r in results],
            "issues": [i for r in results for i in r.issues],
            "errors": errors,
        }

    def sync_batch(
        self,
        politicians: List[Dict[str, Any]],
        *,
        source_names: Optional[List[str]] = None,
        force: bool = False,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        batch = politicians[:limit] if limit and limit > 0 else politicians
        return [
            self.sync_politician(p, source_names=source_names, force=force)
            for p in batch
        ]
