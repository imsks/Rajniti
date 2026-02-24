from __future__ import annotations

import json
import logging
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.agents.base_agent import BaseAgent
from app.core import CacheManager

logger = logging.getLogger(__name__)

BATCH_SIZE = 30
MAX_WORKERS = 3


class ConstituencyFetcher:
    """Subprocess: fetch assembly constituency names for a state."""

    name = "constituencies"

    def __init__(self, agent: BaseAgent):
        self.agent = agent

    def run(self, state: str) -> List[str]:
        logger.info(
            "[ConstituencyFetcher] calling LLM for %s constituencies (this may take ~30s)",
            state,
        )
        prompt = (
            f"Return ONLY a valid JSON array of all current assembly constituency names "
            f"for the Indian state: {state}.\n"
            f'Example format: ["Dispur", "Jalukbari", ...]\n'
        )
        raw = self.agent._run_llm(prompt)
        logger.info("[ConstituencyFetcher] LLM responded (%d chars)", len(raw))

        parsed = self.agent._parse_json_value(raw)
        if parsed is None:
            logger.warning("[ConstituencyFetcher] failed to parse LLM response as JSON")
            return []

        items = self.agent._coerce_to_list(parsed) or []
        result = [c.strip() for c in items if isinstance(c, str) and c.strip()]
        logger.info("[ConstituencyFetcher] parsed %d constituencies", len(result))
        return result


class MLADetailsFetcher:
    """Subprocess: fetch MLA details in parallel batches."""

    name = "mla_details"

    def __init__(
        self,
        agent: BaseAgent,
        batch_size: int = BATCH_SIZE,
        max_workers: int = MAX_WORKERS,
    ):
        self.agent = agent
        self.batch_size = batch_size
        self.max_workers = max_workers

    def _fetch_batch(
        self, state: str, batch: List[str], batch_num: int, total_batches: int
    ) -> List[Dict[str, Any]]:
        tag = f"[MLADetailsFetcher batch {batch_num}/{total_batches}]"
        logger.info("%s fetching %d constituencies", tag, len(batch))

        constituency_json = json.dumps(batch, ensure_ascii=False)
        prompt = (
            f"For each constituency listed below in {state}, return the current MLA.\n"
            f"Return ONLY a valid JSON array. Each item must have: "
            f'"name", "constituency", "party".\n'
            f"Constituencies: {constituency_json}\n"
        )
        raw = self.agent._run_llm(prompt)
        logger.info("%s LLM responded (%d chars)", tag, len(raw))

        parsed = self.agent._parse_json_value(raw)
        if parsed is None:
            logger.warning("%s failed to parse JSON", tag)
            return []

        items = self.agent._coerce_to_list(parsed) or []
        result = [
            d
            for d in items
            if isinstance(d, dict) and d.get("name") and d.get("constituency")
        ]
        logger.info("%s got %d valid records", tag, len(result))
        return result

    def run(self, state: str, constituencies: List[str]) -> List[Dict[str, Any]]:
        batches = [
            constituencies[i : i + self.batch_size]
            for i in range(0, len(constituencies), self.batch_size)
        ]
        total = len(batches)

        if total == 1:
            return self._fetch_batch(state, batches[0], 1, 1)

        logger.info(
            "[MLADetailsFetcher] %d constituencies → %d batches of ~%d (workers=%d)",
            len(constituencies),
            total,
            self.batch_size,
            self.max_workers,
        )

        all_results: List[Dict[str, Any]] = []
        lock = threading.Lock()
        completed = [0]

        def _run_batch(idx: int, batch: List[str]) -> List[Dict[str, Any]]:
            result = self._fetch_batch(state, batch, idx + 1, total)
            with lock:
                completed[0] += 1
                logger.info(
                    "[MLADetailsFetcher] progress: %d/%d batches done (%d records so far)",
                    completed[0],
                    total,
                    len(all_results) + len(result),
                )
            return result

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(_run_batch, i, b): i for i, b in enumerate(batches)
            }
            for future in as_completed(futures):
                try:
                    all_results.extend(future.result())
                except Exception as exc:
                    batch_idx = futures[future]
                    logger.error(
                        "[MLADetailsFetcher] batch %d/%d failed: %s",
                        batch_idx + 1,
                        total,
                        exc,
                    )

        logger.info(
            "[MLADetailsFetcher] all batches done → %d total records", len(all_results)
        )
        return all_results


class StateMLAFetcher(BaseAgent):
    """Orchestrator: fetch + dedupe + persist MLAs for a state."""

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        cache: Optional[CacheManager] = None,
        batch_size: int = BATCH_SIZE,
        max_workers: int = MAX_WORKERS,
    ):
        super().__init__()
        self.data_dir = (
            Path(data_dir) if data_dir else Path(__file__).resolve().parents[1] / "data"
        )
        self.mla_path = self.data_dir / "mla.json"
        self.states_path = self.data_dir / "states.json"
        self.cache = cache or CacheManager()
        self.states = self._load_states()

        self.constituency_fetcher = ConstituencyFetcher(self)
        self.mla_detail_fetcher = MLADetailsFetcher(
            self, batch_size=batch_size, max_workers=max_workers
        )

    def _load_states(self) -> List[str]:
        try:
            return json.loads(self.states_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.error("Failed to load states.json: %s", exc)
            return []

    def _validate_state(self, state: str) -> str:
        norm = state.strip()
        if not norm:
            raise ValueError("state is required")
        for s in self.states:
            if s.lower() == norm.lower():
                return s
        raise ValueError(f"state '{state}' not found in states.json")

    def _load_existing(self) -> List[Dict[str, Any]]:
        if not self.mla_path.exists():
            return []
        try:
            return json.loads(self.mla_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.error("Failed to load mla.json: %s", exc)
            return []

    def _save(self, records: List[Dict[str, Any]]) -> None:
        tmp = self.mla_path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        tmp.replace(self.mla_path)

    @staticmethod
    def _dedupe_key(name: str, constituency: str) -> str:
        return f"{name.strip().lower()}|{constituency.strip().lower()}"

    @staticmethod
    def _make_id(name: str, state: str, constituency: str) -> str:
        payload = f"{name.strip().lower()}|{state.strip().lower()}|{constituency.strip().lower()}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, payload))

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

    def run(self, state: str, force: bool = False) -> Dict[str, Any]:
        state_norm = self._validate_state(state)
        logger.info(
            "[StateMLAFetcher] starting for state: %s (force=%s)", state_norm, force
        )

        logger.info("[Step 1/3] Fetching constituencies for %s", state_norm)
        constituencies = self.constituency_fetcher.run(state_norm)
        if not constituencies:
            logger.warning("[Step 1/3] No constituencies found, aborting")
            return {"ok": False, "error": "no_constituencies_found"}
        logger.info(
            "[Step 1/3] Got %d constituencies for %s", len(constituencies), state_norm
        )

        logger.info(
            "[Step 2/3] Fetching MLA details for %d constituencies", len(constituencies)
        )
        fetched = self.mla_detail_fetcher.run(state_norm, constituencies)
        if not fetched:
            logger.warning("[Step 2/3] No MLA data fetched, aborting")
            return {"ok": False, "error": "no_mla_data_fetched"}
        logger.info("[Step 2/3] Got %d MLA records", len(fetched))

        logger.info("[Step 3/3] Deduplicating and persisting records")
        existing = self._load_existing()
        seen = {
            self._dedupe_key(p.get("name", ""), p.get("constituency", "")): p
            for p in existing
        }
        added, skipped_cached, skipped_duplicate = 0, 0, 0

        for item in fetched:
            name = (item.get("name") or "").strip()
            constituency = (item.get("constituency") or "").strip()
            if not name or not constituency:
                continue

            pid = self._make_id(name, state_norm, constituency)

            if self.cache.exists(pid) and not force:
                skipped_cached += 1
                continue

            dkey = self._dedupe_key(name, constituency)
            if dkey in seen and not force:
                skipped_duplicate += 1
                continue

            record = {
                "id": pid,
                "name": name,
                "photo": item.get("photo"),
                "state": state_norm,
                "constituency": constituency,
                "party": item.get("party"),
                "type": "MLA",
                "education": None,
                "family_background": None,
                "criminal_records": None,
                "social_media": None,
                "contact": None,
                "political_background": {"elections": [], "summary": None},
                "notes": None,
            }

            existing.append(record)
            seen[dkey] = record
            added += 1
            self.cache.set(pid, {"fetched": True})

        if added:
            self._save(existing)
            logger.info("[Step 3/3] Saved %d new records to mla.json", added)
        else:
            logger.info("[Step 3/3] No new records to save")

        if skipped_cached or skipped_duplicate:
            logger.info(
                "[Step 3/3] Skipped: %d cached, %d duplicate",
                skipped_cached,
                skipped_duplicate,
            )

        summary = {
            "ok": True,
            "state": state_norm,
            "constituencies_found": len(constituencies),
            "fetched": len(fetched),
            "added": added,
            "skipped_cached": skipped_cached,
            "skipped_duplicate": skipped_duplicate,
            "total_now": len(existing),
        }
        logger.info("[StateMLAFetcher] done: %s", summary)
        return summary
