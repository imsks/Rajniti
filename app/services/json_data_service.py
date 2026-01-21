"""
JSON Data Service Implementation

This DataService reads election data directly from the JSON datasets under
`app/data/**/<election_id>/`.

Why this exists:
- You can run the API without a database.
- Candidate enrichment agents can write detailed fields back into candidates.json,
  and the API will serve them immediately.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .data_service import DataService

logger = logging.getLogger(__name__)


class JsonDataService(DataService):
    """JSON-backed data service implementation."""

    def __init__(self, base_data_dir: Optional[Path] = None):
        self.base_data_dir = (
            base_data_dir
            if base_data_dir is not None
            else Path(__file__).resolve().parents[1] / "data"
        )
        self.elections_dir = self.base_data_dir / "elections"

        # Cache: filepath -> (mtime_ns, parsed_json)
        self._file_cache: Dict[Path, Tuple[int, Any]] = {}

        # election_id -> dataset directory (parent of candidates.json)
        self._election_dirs: Dict[str, Path] = {}
        self._index_election_dirs()

        # Cache for election metadata list
        self._elections_cache: Optional[List[Dict[str, Any]]] = None

    def _index_election_dirs(self) -> None:
        """Index dataset directories by looking for candidates.json files."""
        self._election_dirs = {}
        if not self.base_data_dir.exists():
            logger.warning("JSON data dir not found: %s", self.base_data_dir)
            return

        for candidates_file in self.base_data_dir.rglob("candidates.json"):
            election_dir = candidates_file.parent
            self._election_dirs[election_dir.name] = election_dir

    def _read_json_cached(self, path: Path, default: Any) -> Any:
        """Read JSON from disk with a simple mtime-based cache."""
        if not path.exists():
            return default

        try:
            mtime_ns = path.stat().st_mtime_ns
        except OSError:
            return default

        cached = self._file_cache.get(path)
        if cached and cached[0] == mtime_ns:
            return cached[1]

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.warning("Failed to read JSON %s: %s", path, e)
            return default

        self._file_cache[path] = (mtime_ns, data)
        return data

    def _resolve_election_dir(self, election_id: str) -> Optional[Path]:
        election_dir = self._election_dirs.get(election_id)
        if election_dir and election_dir.exists():
            return election_dir

        # Re-index once if not found (supports new datasets created at runtime).
        self._index_election_dirs()
        election_dir = self._election_dirs.get(election_id)
        if election_dir and election_dir.exists():
            return election_dir

        return None

    def _paths_for_election(self, election_id: str) -> Optional[Dict[str, Path]]:
        election_dir = self._resolve_election_dir(election_id)
        if not election_dir:
            return None

        return {
            "dir": election_dir,
            "candidates": election_dir / "candidates.json",
            "parties": election_dir / "parties.json",
            "constituencies": election_dir / "constituencies.json",
        }

    # ---- DataService interface ----

    def get_elections(self) -> List[Dict[str, Any]]:
        if self._elections_cache is not None:
            return self._elections_cache

        elections: List[Dict[str, Any]] = []
        if not self.elections_dir.exists():
            self._elections_cache = []
            return []

        for f in sorted(self.elections_dir.glob("*.json")):
            payload = self._read_json_cached(f, default=[])
            if not isinstance(payload, list):
                continue
            for item in payload:
                if not isinstance(item, dict):
                    continue
                election_id = item.get("election_id") or item.get("id")
                if not election_id:
                    continue
                normalized = item.copy()
                normalized["id"] = election_id
                elections.append(normalized)

        self._elections_cache = elections
        return elections

    def get_election(self, election_id: str) -> Optional[Dict[str, Any]]:
        for e in self.get_elections():
            if e.get("id") == election_id:
                return e
        return None

    def get_candidates(self, election_id: str) -> List[Dict[str, Any]]:
        paths = self._paths_for_election(election_id)
        if not paths:
            return []
        data = self._read_json_cached(paths["candidates"], default=[])
        if not isinstance(data, list):
            return []
        # Filter out NOTA entries
        return [c for c in data if isinstance(c, dict) and c.get("name") != "NOTA"]

    def get_parties(self, election_id: str) -> List[Dict[str, Any]]:
        paths = self._paths_for_election(election_id)
        if not paths:
            return []
        data = self._read_json_cached(paths["parties"], default=[])
        return data if isinstance(data, list) else []

    def get_constituencies(self, election_id: str) -> List[Dict[str, Any]]:
        paths = self._paths_for_election(election_id)
        if not paths:
            return []
        data = self._read_json_cached(paths["constituencies"], default=[])
        return data if isinstance(data, list) else []

    def search_candidates(
        self, query: str, election_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        election_id = election_id or "lok-sabha-2024"
        q = (query or "").strip().lower()
        if not q:
            return []

        parties = {str(p.get("id")): p for p in self.get_parties(election_id) if isinstance(p, dict)}
        constituencies = {
            str(c.get("id")): c for c in self.get_constituencies(election_id) if isinstance(c, dict)
        }

        results: List[Dict[str, Any]] = []
        for cand in self.get_candidates(election_id):
            name = str(cand.get("name", "")).lower()
            party = parties.get(str(cand.get("party_id")))
            party_name = str((party or {}).get("name", "")).lower()
            party_short = str((party or {}).get("short_name", "")).lower()
            constituency = constituencies.get(str(cand.get("constituency_id")))
            constituency_name = str((constituency or {}).get("name", "")).lower()

            if (
                q in name
                or (party_name and q in party_name)
                or (party_short and q in party_short)
                or (constituency_name and q in constituency_name)
            ):
                results.append(self.enrich_candidate_data(cand, election_id))

        # Sort: name matches first, then winners, then name
        results.sort(
            key=lambda x: (
                q not in str(x.get("name", "")).lower(),
                x.get("status") != "WON",
                str(x.get("name", "")),
            )
        )
        return results

    def get_candidate_by_id(
        self, candidate_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        for cand in self.get_candidates(election_id):
            if cand.get("id") == candidate_id:
                return self.enrich_candidate_data(cand, election_id)
        return None

    def get_candidate_by_id_only(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        # Preserve existing API behavior.
        return self.get_candidate_by_id(candidate_id, election_id="lok-sabha-2024")

    def get_party_by_name(
        self, party_name: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        q = (party_name or "").strip().lower()
        if not q:
            return None
        for party in self.get_parties(election_id):
            if str(party.get("name", "")).strip().lower() == q:
                return party
            if str(party.get("short_name", "")).strip().lower() == q:
                return party
        return None

    def get_constituency_by_id(
        self, constituency_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        for c in self.get_constituencies(election_id):
            if c.get("id") == constituency_id:
                return c
        return None

    # ---- Enrichment & derived views ----

    def enrich_candidate_data(
        self, candidate: Dict[str, Any], election_id: str
    ) -> Dict[str, Any]:
        parties = {str(p.get("id")): p for p in self.get_parties(election_id) if isinstance(p, dict)}
        constituencies = {
            str(c.get("id")): c for c in self.get_constituencies(election_id) if isinstance(c, dict)
        }

        party = parties.get(str(candidate.get("party_id"))) or {}
        constituency = constituencies.get(str(candidate.get("constituency_id"))) or {}

        state_id = candidate.get("state_id") or constituency.get("state_id")
        enriched = candidate.copy()
        enriched.update(
            {
                "election_id": election_id,
                "party_name": party.get("name", "Unknown"),
                "party_short_name": party.get("short_name", "UNK"),
                "party_symbol": party.get("symbol", ""),
                "constituency_name": constituency.get("name", "Unknown"),
                "constituency_state_id": constituency.get("state_id", ""),
                "state_name": self.get_state_name(str(state_id)) if state_id else "Unknown",
            }
        )
        return enriched

    def get_state_name(self, state_id: str) -> str:
        # Keep this conservative; a dedicated mapping file/table can be added later.
        return state_id

    def get_election_statistics(self, election_id: str) -> Dict[str, int]:
        candidates = self.get_candidates(election_id)
        parties = self.get_parties(election_id)
        constituencies = self.get_constituencies(election_id)

        total_candidates = len(candidates)
        total_winners = sum(1 for c in candidates if c.get("status") == "WON")

        return {
            "total_candidates": total_candidates,
            "total_parties": len(parties),
            "total_constituencies": len(constituencies),
            "total_winners": total_winners,
        }

    def get_party_seat_counts(
        self, election_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        parties = {str(p.get("id")): p for p in self.get_parties(election_id) if isinstance(p, dict)}

        seats: Dict[str, int] = {}
        for c in self.get_candidates(election_id):
            if c.get("status") == "WON":
                pid = str(c.get("party_id", "UNKNOWN"))
                seats[pid] = seats.get(pid, 0) + 1

        ranked = sorted(seats.items(), key=lambda x: x[1], reverse=True)[:limit]
        result: List[Dict[str, Any]] = []
        for pid, seats_won in ranked:
            party = parties.get(pid) or {}
            result.append(
                {
                    "party_name": party.get("name", "INDEPENDENT" if pid == "UNKNOWN" else pid),
                    "party_short_name": party.get(
                        "short_name", "IND" if pid == "UNKNOWN" else pid
                    ),
                    "seats_won": seats_won,
                }
            )
        return result

