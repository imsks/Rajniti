from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.agents.base_agent import BaseAgent
from app.core import CacheManager

logger = logging.getLogger(__name__)


class ConstituencyFetcher:
    """Subprocess: fetch assembly constituency names for a state."""

    name = "constituencies"

    def __init__(self, agent: BaseAgent):
        self.agent = agent

    def run(self, state: str) -> List[str]:
        logger.info("[ConstituencyFetcher] calling LLM for %s constituencies", state)
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
    """Subprocess: fetch MLA details for given constituencies."""

    name = "mla_details"

    def __init__(self, agent: BaseAgent):
        self.agent = agent

    def run(self, state: str, constituencies: List[str]) -> List[Dict[str, Any]]:
        logger.info("[MLADetailsFetcher] calling LLM for %d constituencies in %s", len(constituencies), state)
        constituency_json = json.dumps(constituencies, ensure_ascii=False)
        prompt = (
            f"For each constituency listed below in {state}, return the current MLA.\n"
            f"Return ONLY a valid JSON array. Each item must have: "
            f'"name", "constituency", "party".\n'
            f"Constituencies: {constituency_json}\n"
        )
        raw = self.agent._run_llm(prompt)
        logger.info("[MLADetailsFetcher] LLM responded (%d chars)", len(raw))

        parsed = self.agent._parse_json_value(raw)
        if parsed is None:
            logger.warning("[MLADetailsFetcher] failed to parse LLM response as JSON")
            return []

        items = self.agent._coerce_to_list(parsed) or []
        result = [
            d for d in items
            if isinstance(d, dict) and d.get("name") and d.get("constituency")
        ]
        logger.info("[MLADetailsFetcher] parsed %d valid MLA records out of %d items", len(result), len(items))
        return result


class StateMLAFetcher(BaseAgent):
    """Orchestrator: fetch + dedupe + persist MLAs for a state."""

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        cache: Optional[CacheManager] = None,
    ):
        super().__init__()
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parents[1] / "data"
        self.mla_path = self.data_dir / "mla.json"
        self.states_path = self.data_dir / "states.json"
        self.cache = cache or CacheManager()
        self.states = self._load_states()

        self.constituency_fetcher = ConstituencyFetcher(self)
        self.mla_detail_fetcher = MLADetailsFetcher(self)

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
        tmp.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.mla_path)

    @staticmethod
    def _dedupe_key(name: str, constituency: str) -> str:
        return f"{name.strip().lower()}|{constituency.strip().lower()}"

    @staticmethod
    def _make_id(name: str, state: str, constituency: str) -> str:
        payload = f"{name.strip().lower()}|{state.strip().lower()}|{constituency.strip().lower()}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, payload))

    def run(self, state: str, force: bool = False) -> Dict[str, Any]:
        state_norm = self._validate_state(state)
        logger.info("[StateMLAFetcher] starting for state: %s (force=%s)", state_norm, force)

        logger.info("[Step 1/3] Fetching constituencies for %s", state_norm)
        constituencies = self.constituency_fetcher.run(state_norm)
        if not constituencies:
            logger.warning("[Step 1/3] No constituencies found, aborting")
            return {"ok": False, "error": "no_constituencies_found"}
        logger.info("[Step 1/3] Got %d constituencies for %s", len(constituencies), state_norm)

        logger.info("[Step 2/3] Fetching MLA details for %d constituencies", len(constituencies))
        fetched = self.mla_detail_fetcher.run(state_norm, constituencies)
        if not fetched:
            logger.warning("[Step 2/3] No MLA data fetched, aborting")
            return {"ok": False, "error": "no_mla_data_fetched"}
        logger.info("[Step 2/3] Got %d MLA records", len(fetched))

        logger.info("[Step 3/3] Deduplicating and persisting records")
        existing = self._load_existing()
        seen = {self._dedupe_key(p.get("name", ""), p.get("constituency", "")): p for p in existing}
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
            logger.info("[Step 3/3] Skipped: %d cached, %d duplicate", skipped_cached, skipped_duplicate)

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
