from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.agents.base_agent import BaseAgent
from app.core import CacheManager

logger = logging.getLogger(__name__)


class StateMLAFetcher(BaseAgent):
    """Orchestrator: fetch + dedupe + persist MLAs for a state.

    Delegates actual work to the simple queue-based fetcher in
    app.agents.mla_fetcher.run_fetcher().
    """

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        cache: Optional[CacheManager] = None,
    ):
        super().__init__()
        self.data_dir = (
            Path(data_dir) if data_dir else Path(__file__).resolve().parents[1] / "data"
        )
        self.mla_path = self.data_dir / "mla.json"
        self.states_path = self.data_dir / "states.json"
        self.cache = cache or CacheManager()
        self.states = self._load_states()

    def _load_states(self) -> List[str]:
        try:
            return json.loads(self.states_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.error("Failed to load states.json: %s", exc)
            return []

    def run_all(self, force: bool = False) -> Dict[str, Any]:
        logger.info(
            "[StateMLAFetcher] running for ALL %d states (force=%s)",
            len(self.states),
            force,
        )
        results: List[Dict[str, Any]] = []
        for idx, state in enumerate(self.states, 1):
            logger.info("[StateMLAFetcher] [%d/%d] %s", idx, len(self.states), state)
            result = self.run(state, force=force)
            results.append(result)
            status = "ok" if result.get("ok") else "FAILED"
            added = result.get("added", 0)
            logger.info(
                "[StateMLAFetcher] [%d/%d] %s → %s (added=%d)",
                idx,
                len(self.states),
                state,
                status,
                added,
            )

        total_added = sum(r.get("added", 0) for r in results)
        succeeded = sum(1 for r in results if r.get("ok"))
        failed = len(results) - succeeded
        summary = {
            "ok": failed == 0,
            "states_total": len(results),
            "states_succeeded": succeeded,
            "states_failed": failed,
            "total_added": total_added,
        }
        logger.info("[StateMLAFetcher] all states done: %s", summary)
        return summary

    def run(self, state: str, force: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """Run the MLA fetcher for a single state using the simple queue approach."""
        logger.warning(
            "StateMLAFetcher uses LLM-generated constituency lists (deprecated). "
            "Prefer: scripts/scrape_election.py (ECI) then scripts/scrape_politician_sources.py"
        )
        from app.agents.mla_fetcher import run_fetcher

        try:
            result = run_fetcher(
                agent=self,
                state=state,
                data_dir=self.data_dir,
                force=force,
                dry_run=dry_run,
            )

            return {
                "ok": result.ok,
                "state": result.state,
                "constituencies_found": result.constituencies_found,
                "fetched": result.fetched,
                "added": result.added,
                "skipped": result.skipped,
                "error": result.error,
            }

        except Exception as exc:
            logger.error("[StateMLAFetcher] Failed for %s: %s", state, exc)
            return {"ok": False, "state": state, "error": str(exc)}
