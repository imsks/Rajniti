"""
JSON Data Service Implementation

Reads election data directly from JSON files.
This is the primary data source for elections/candidates/parties/constituencies.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .data_service import DataService

logger = logging.getLogger(__name__)

# State ID to State Name mapping (used by controllers/UI)
STATE_NAMES: Dict[str, str] = {
    # Lok Sabha scraper-style state ids
    "S01": "Andhra Pradesh",
    "S02": "Arunachal Pradesh",
    "S03": "Assam",
    "S04": "Bihar",
    "S05": "Goa",
    "S06": "Gujarat",
    "S07": "Haryana",
    "S08": "Himachal Pradesh",
    "S09": "Jammu and Kashmir",
    "S10": "Karnataka",
    "S11": "Kerala",
    "S12": "Madhya Pradesh",
    "S13": "Maharashtra",
    "S14": "Manipur",
    "S15": "Meghalaya",
    "S16": "Mizoram",
    "S17": "Nagaland",
    "S18": "Odisha",
    "S19": "Punjab",
    "S20": "Rajasthan",
    "S21": "Sikkim",
    "S22": "Tamil Nadu",
    "S23": "Tripura",
    "S24": "Uttar Pradesh",
    "S25": "West Bengal",
    "S26": "Chhattisgarh",
    "S27": "Jharkhand",
    "S28": "Uttarakhand",
    "S29": "Telangana",
    # Union territories
    "U01": "Andaman and Nicobar Islands",
    "U02": "Chandigarh",
    "U03": "Dadra and Nagar Haveli and Daman and Diu",
    "U05": "Delhi",
    "U06": "Lakshadweep",
    "U07": "Puducherry",
    "U08": "Ladakh",
    # Common short codes (Vidhan Sabha + others)
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CG": "Chhattisgarh",
    "DL": "Delhi",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HP": "Himachal Pradesh",
    "HR": "Haryana",
    "JH": "Jharkhand",
    "JK": "Jammu and Kashmir",
    "KA": "Karnataka",
    "KL": "Kerala",
    "MH": "Maharashtra",
    "ML": "Meghalaya",
    "MN": "Manipur",
    "MP": "Madhya Pradesh",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OR": "Odisha",
    "PB": "Punjab",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TG": "Telangana",
    "TN": "Tamil Nadu",
    "TR": "Tripura",
    "UK": "Uttarakhand",
    "UP": "Uttar Pradesh",
    "WB": "West Bengal",
}


class JsonDataService(DataService):
    """JSON file-backed data service implementation."""

    def __init__(self, data_dir: Optional[Path] = None):
        self._data_dir = Path(data_dir) if data_dir is not None else Path(__file__).parent.parent / "data"

        # Caches for performance
        self._elections_cache: Optional[List[Dict[str, Any]]] = None
        self._parties_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._constituencies_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._candidates_cache: Dict[str, List[Dict[str, Any]]] = {}

    # ---- IO helpers ----

    def _load_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        if not file_path.exists():
            return []
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [x for x in data if isinstance(x, dict)]
            if isinstance(data, dict):
                return [data]
            return []
        except Exception as e:
            logger.warning("Failed to read JSON %s: %s", file_path, e)
            return []

    def _get_election_data_dir(self, election_id: str) -> Optional[Path]:
        # Lok Sabha
        lok = self._data_dir / "lok_sabha" / election_id
        if lok.exists():
            return lok

        # Vidhan Sabha
        vs = self._data_dir / "vidhan_sabha" / election_id
        if vs.exists():
            return vs

        # Loose match for vidhan sabha folders (e.g., CG_2025_ASSEMBLY)
        vs_root = self._data_dir / "vidhan_sabha"
        if vs_root.exists():
            for d in vs_root.glob("*"):
                if d.is_dir() and election_id in d.name:
                    return d

        return None

    # ---- DataService interface ----

    def get_elections(self) -> List[Dict[str, Any]]:
        if self._elections_cache is not None:
            return self._elections_cache

        elections_dir = self._data_dir / "elections"
        elections: List[Dict[str, Any]] = []
        if elections_dir.exists():
            for f in elections_dir.glob("*.json"):
                for item in self._load_json_file(f):
                    eid = item.get("election_id") or item.get("id") or f.stem
                    normalized = item.copy()
                    normalized["id"] = eid
                    elections.append(normalized)

        self._elections_cache = elections
        return elections

    def get_election(self, election_id: str) -> Optional[Dict[str, Any]]:
        for e in self.get_elections():
            if e.get("id") == election_id:
                return e
        return None

    def get_candidates(self, election_id: str) -> List[Dict[str, Any]]:
        if election_id in self._candidates_cache:
            return self._candidates_cache[election_id]

        data_dir = self._get_election_data_dir(election_id)
        if not data_dir:
            self._candidates_cache[election_id] = []
            return []

        candidates = self._load_json_file(data_dir / "candidates.json")
        candidates = [c for c in candidates if c.get("name") != "NOTA"]
        self._candidates_cache[election_id] = candidates
        return candidates

    def get_parties(self, election_id: str) -> List[Dict[str, Any]]:
        if election_id in self._parties_cache:
            return self._parties_cache[election_id]

        data_dir = self._get_election_data_dir(election_id)
        if not data_dir:
            self._parties_cache[election_id] = []
            return []

        parties = self._load_json_file(data_dir / "parties.json")
        self._parties_cache[election_id] = parties
        return parties

    def get_constituencies(self, election_id: str) -> List[Dict[str, Any]]:
        if election_id in self._constituencies_cache:
            return self._constituencies_cache[election_id]

        data_dir = self._get_election_data_dir(election_id)
        if not data_dir:
            self._constituencies_cache[election_id] = []
            return []

        constituencies = self._load_json_file(data_dir / "constituencies.json")
        self._constituencies_cache[election_id] = constituencies
        return constituencies

    def search_candidates(
        self, query: str, election_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        election_id = election_id or "lok-sabha-2024"
        q = (query or "").strip().lower()
        if not q:
            return []

        parties = {p.get("id"): p for p in self.get_parties(election_id)}
        constituencies = {c.get("id"): c for c in self.get_constituencies(election_id)}

        results: List[Dict[str, Any]] = []
        for cand in self.get_candidates(election_id):
            name = str(cand.get("name", "")).lower()
            party = parties.get(cand.get("party_id")) or {}
            constituency = constituencies.get(cand.get("constituency_id")) or {}
            party_name = str(party.get("name", "")).lower()
            party_short = str(party.get("short_name", "")).lower()
            constituency_name = str(constituency.get("name", "")).lower()

            if (
                q in name
                or (party_name and q in party_name)
                or (party_short and q in party_short)
                or (constituency_name and q in constituency_name)
            ):
                results.append(self.enrich_candidate_data(cand, election_id))

        return results

    def get_candidate_by_id(
        self, candidate_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        for cand in self.get_candidates(election_id):
            if cand.get("id") == candidate_id:
                return self.enrich_candidate_data(cand, election_id)
        return None

    def get_candidate_by_id_only(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        return self.get_candidate_by_id(candidate_id, "lok-sabha-2024")

    def get_party_by_name(self, party_name: str, election_id: str) -> Optional[Dict[str, Any]]:
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

    # ---- Additional methods used by controllers ----

    def enrich_candidate_data(self, candidate: Dict[str, Any], election_id: str) -> Dict[str, Any]:
        parties = {p.get("id"): p for p in self.get_parties(election_id)}
        constituencies = {c.get("id"): c for c in self.get_constituencies(election_id)}

        party = parties.get(candidate.get("party_id")) or {}
        constituency = constituencies.get(candidate.get("constituency_id")) or {}
        state_id = candidate.get("state_id") or constituency.get("state_id") or ""

        enriched = candidate.copy()
        enriched.update(
            {
                "election_id": election_id,
                "party_name": party.get("name", "Unknown"),
                "party_short_name": party.get("short_name", "UNK"),
                "party_symbol": party.get("symbol", ""),
                "constituency_name": constituency.get("name", "Unknown"),
                "constituency_state_id": constituency.get("state_id", ""),
                "state_name": self.get_state_name(str(state_id)),
            }
        )
        return enriched

    def get_state_name(self, state_id: str) -> str:
        if not state_id:
            return "Unknown"
        return STATE_NAMES.get(state_id, "Unknown")

    def get_election_statistics(self, election_id: str) -> Dict[str, int]:
        candidates = self.get_candidates(election_id)
        parties = self.get_parties(election_id)
        constituencies = self.get_constituencies(election_id)

        return {
            "total_candidates": len(candidates),
            "total_parties": len(parties),
            "total_constituencies": len(constituencies),
            "total_winners": sum(1 for c in candidates if c.get("status") == "WON"),
        }

    def get_party_seat_counts(self, election_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        seats: Dict[str, int] = {}
        for c in self.get_candidates(election_id):
            if c.get("status") == "WON":
                pid = c.get("party_id", "UNKNOWN")
                seats[pid] = seats.get(pid, 0) + 1

        ranked = sorted(seats.items(), key=lambda x: x[1], reverse=True)[:limit]
        parties = {p.get("id"): p for p in self.get_parties(election_id)}

        result: List[Dict[str, Any]] = []
        for pid, seats_won in ranked:
            party = parties.get(pid) or {}
            result.append(
                {
                    "party_name": party.get("name", pid),
                    "party_short_name": party.get("short_name", pid),
                    "seats_won": seats_won,
                }
            )
        return result

    # ---- Helper methods ----

    def clear_cache(self) -> None:
        self._elections_cache = None
        self._parties_cache = {}
        self._constituencies_cache = {}
        self._candidates_cache = {}

    def reload_election_data(self, election_id: str) -> None:
        self._parties_cache.pop(election_id, None)
        self._constituencies_cache.pop(election_id, None)
        self._candidates_cache.pop(election_id, None)

