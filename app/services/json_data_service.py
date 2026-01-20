"""
JSON Data Service Implementation

Reads election data directly from JSON files.
Replaces the database-backed service for static election data.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .data_service import DataService

logger = logging.getLogger(__name__)


# State ID to State Name mapping
STATE_NAMES = {
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
    "U01": "Andaman and Nicobar Islands",
    "U02": "Chandigarh",
    "U03": "Dadra and Nagar Haveli and Daman and Diu",
    "U05": "Delhi",
    "U06": "Lakshadweep",
    "U07": "Puducherry",
    "U08": "Ladakh",
    # Short codes used in some elections
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
        """
        Initialize JSON data service with caching.

        Args:
            data_dir: Base directory for data files. Defaults to app/data
        """
        if data_dir is None:
            # Default to app/data relative to this file
            self._data_dir = Path(__file__).parent.parent / "data"
        else:
            self._data_dir = Path(data_dir)

        # Caches for performance
        self._elections_cache: Optional[List[Dict[str, Any]]] = None
        self._election_data_cache: Dict[str, Dict[str, Any]] = {}
        self._parties_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._constituencies_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._candidates_cache: Dict[str, List[Dict[str, Any]]] = {}

        logger.info(f"JsonDataService initialized with data_dir: {self._data_dir}")

    def _load_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load data from a JSON file."""
        if not file_path.exists():
            logger.warning(f"JSON file not found: {file_path}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return []

    def _get_election_data_dir(self, election_id: str) -> Optional[Path]:
        """
        Get the data directory for a specific election.

        Supports multiple election types:
        - lok_sabha: app/data/lok_sabha/{election_id}/
        - vidhan_sabha: app/data/vidhan_sabha/{election_id}/
        """
        # Try lok_sabha first
        lok_sabha_dir = self._data_dir / "lok_sabha" / election_id
        if lok_sabha_dir.exists():
            return lok_sabha_dir

        # Try vidhan_sabha
        vidhan_sabha_dir = self._data_dir / "vidhan_sabha" / election_id
        if vidhan_sabha_dir.exists():
            return vidhan_sabha_dir

        # Check if it matches a vidhan sabha folder pattern
        for vs_dir in (self._data_dir / "vidhan_sabha").glob("*"):
            if vs_dir.is_dir() and election_id in vs_dir.name:
                return vs_dir

        logger.warning(f"Election data directory not found for: {election_id}")
        return None

    def _load_all_elections(self) -> List[Dict[str, Any]]:
        """Load all election metadata from elections directory."""
        elections = []
        elections_dir = self._data_dir / "elections"

        if not elections_dir.exists():
            logger.warning(f"Elections directory not found: {elections_dir}")
            return elections

        for json_file in elections_dir.glob("*.json"):
            file_elections = self._load_json_file(json_file)
            for election in file_elections:
                # Normalize election data
                elections.append({
                    "id": election.get("election_id", json_file.stem),
                    "name": election.get("name", ""),
                    "type": election.get("type", ""),
                    "year": election.get("year", 0),
                    "state_id": election.get("state_id"),
                    "state_name": election.get("state_name"),
                    "total_constituencies": election.get("total_constituencies", 0),
                    "total_candidates": election.get("total_candidates", 0),
                    "total_parties": election.get("total_parties", 0),
                    "result_status": election.get("result_status"),
                    "winning_party": election.get("winning_party"),
                    "winning_party_seats": election.get("winning_party_seats"),
                })

        return elections

    # ==================== DataService Interface Implementation ====================

    def get_elections(self) -> List[Dict[str, Any]]:
        """Get all available elections."""
        if self._elections_cache is None:
            self._elections_cache = self._load_all_elections()
        return self._elections_cache

    def get_election(self, election_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific election by ID."""
        elections = self.get_elections()
        for election in elections:
            if election["id"] == election_id:
                return election
        return None

    def get_candidates(self, election_id: str) -> List[Dict[str, Any]]:
        """Get all candidates for an election."""
        if election_id in self._candidates_cache:
            return self._candidates_cache[election_id]

        data_dir = self._get_election_data_dir(election_id)
        if not data_dir:
            return []

        candidates_file = data_dir / "candidates.json"
        candidates = self._load_json_file(candidates_file)

        # Filter out NOTA entries
        candidates = [c for c in candidates if c.get("name") != "NOTA"]

        self._candidates_cache[election_id] = candidates
        return candidates

    def get_parties(self, election_id: str) -> List[Dict[str, Any]]:
        """Get all parties for an election."""
        if election_id in self._parties_cache:
            return self._parties_cache[election_id]

        data_dir = self._get_election_data_dir(election_id)
        if not data_dir:
            return []

        parties_file = data_dir / "parties.json"
        parties = self._load_json_file(parties_file)

        self._parties_cache[election_id] = parties
        return parties

    def get_constituencies(self, election_id: str) -> List[Dict[str, Any]]:
        """Get all constituencies for an election."""
        if election_id in self._constituencies_cache:
            return self._constituencies_cache[election_id]

        data_dir = self._get_election_data_dir(election_id)
        if not data_dir:
            return []

        constituencies_file = data_dir / "constituencies.json"
        constituencies = self._load_json_file(constituencies_file)

        self._constituencies_cache[election_id] = constituencies
        return constituencies

    def search_candidates(
        self, query: str, election_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search candidates by name, party, or constituency."""
        query_lower = query.lower()
        results = []

        # If no election_id, search across all elections
        if election_id:
            election_ids = [election_id]
        else:
            election_ids = [e["id"] for e in self.get_elections()]

        for eid in election_ids:
            candidates = self.get_candidates(eid)
            parties = {p["id"]: p for p in self.get_parties(eid)}
            constituencies = {c.get("unique_id", c["id"]): c for c in self.get_constituencies(eid)}

            for candidate in candidates:
                # Search in name
                if query_lower in candidate.get("name", "").lower():
                    results.append(self._enrich_candidate(candidate, eid, parties, constituencies))
                    continue

                # Search in party name
                party = parties.get(candidate.get("party_id"))
                if party and (
                    query_lower in party.get("name", "").lower()
                    or query_lower in party.get("short_name", "").lower()
                ):
                    results.append(self._enrich_candidate(candidate, eid, parties, constituencies))
                    continue

                # Search in constituency name
                const_id = candidate.get("constituency_unique_id") or candidate.get("constituency_id")
                constituency = constituencies.get(const_id)
                if constituency and query_lower in constituency.get("name", "").lower():
                    results.append(self._enrich_candidate(candidate, eid, parties, constituencies))

        return results

    def get_candidate_by_id(
        self, candidate_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific candidate."""
        candidates = self.get_candidates(election_id)
        parties = {p["id"]: p for p in self.get_parties(election_id)}
        constituencies = {c.get("unique_id", c["id"]): c for c in self.get_constituencies(election_id)}

        for candidate in candidates:
            if candidate.get("id") == candidate_id:
                return self._enrich_candidate(
                    candidate, election_id, parties, constituencies, include_details=True
                )
        return None

    def get_candidate_by_id_only(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific candidate without election_id."""
        # Search across all elections
        for election in self.get_elections():
            candidate = self.get_candidate_by_id(candidate_id, election["id"])
            if candidate:
                return candidate
        return None

    def get_party_by_name(
        self, party_name: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific party."""
        parties = self.get_parties(election_id)
        party_name_lower = party_name.lower()

        for party in parties:
            if (
                party.get("name", "").lower() == party_name_lower
                or party.get("short_name", "").lower() == party_name_lower
            ):
                return party
        return None

    def get_constituency_by_id(
        self, constituency_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific constituency."""
        constituencies = self.get_constituencies(election_id)

        for constituency in constituencies:
            if (
                constituency.get("id") == constituency_id
                or constituency.get("unique_id") == constituency_id
            ):
                return constituency
        return None

    # ==================== Additional Methods Used by Controllers ====================

    def get_state_name(self, state_id: str) -> str:
        """Get state name from state ID."""
        if not state_id:
            return "Unknown"
        return STATE_NAMES.get(state_id.upper(), STATE_NAMES.get(state_id, "Unknown"))

    def enrich_candidate_data(
        self, candidate: Dict[str, Any], election_id: str
    ) -> Dict[str, Any]:
        """
        Enrich candidate data with party and constituency information.

        Args:
            candidate: Raw candidate dictionary
            election_id: Election ID

        Returns:
            Enriched candidate dictionary
        """
        parties = {p["id"]: p for p in self.get_parties(election_id)}
        constituencies = {c.get("unique_id", c["id"]): c for c in self.get_constituencies(election_id)}

        return self._enrich_candidate(candidate, election_id, parties, constituencies)

    def get_election_statistics(self, election_id: str) -> Dict[str, int]:
        """
        Get statistics for an election.

        Returns:
            Dictionary with total_candidates, total_parties, total_constituencies, total_winners
        """
        candidates = self.get_candidates(election_id)
        parties = self.get_parties(election_id)
        constituencies = self.get_constituencies(election_id)

        total_winners = sum(1 for c in candidates if c.get("status") == "WON")

        return {
            "total_candidates": len(candidates),
            "total_parties": len(parties),
            "total_constituencies": len(constituencies),
            "total_winners": total_winners,
        }

    def get_party_seat_counts(
        self, election_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get party-wise seat counts.

        Returns:
            List of top parties by seats won
        """
        candidates = self.get_candidates(election_id)
        parties = {p["id"]: p for p in self.get_parties(election_id)}

        # Count seats per party
        party_seats: Dict[str, int] = {}
        for candidate in candidates:
            if candidate.get("status") == "WON":
                party_id = candidate.get("party_id", "UNKNOWN")
                party_seats[party_id] = party_seats.get(party_id, 0) + 1

        # Sort by seats won (descending)
        sorted_parties = sorted(party_seats.items(), key=lambda x: x[1], reverse=True)

        # Build result
        result = []
        for party_id, seats_won in sorted_parties[:limit]:
            party = parties.get(party_id)
            if party:
                result.append({
                    "party_name": party.get("name", "Unknown"),
                    "party_short_name": party.get("short_name", "UNK"),
                    "seats_won": seats_won,
                })
            else:
                result.append({
                    "party_name": "INDEPENDENT",
                    "party_short_name": "IND",
                    "seats_won": seats_won,
                })

        return result

    # ==================== Helper Methods ====================

    def _enrich_candidate(
        self,
        candidate: Dict[str, Any],
        election_id: str,
        parties: Dict[str, Dict[str, Any]],
        constituencies: Dict[str, Dict[str, Any]],
        include_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Enrich candidate data with party and constituency details.

        Args:
            candidate: Raw candidate dictionary
            election_id: Election ID
            parties: Dictionary of party_id -> party data
            constituencies: Dictionary of constituency_id -> constituency data
            include_details: Whether to include detailed fields

        Returns:
            Enriched candidate dictionary
        """
        party_id = candidate.get("party_id", "UNKNOWN")
        party = parties.get(party_id)

        const_id = candidate.get("constituency_unique_id") or candidate.get("constituency_id")
        constituency = constituencies.get(const_id)

        result = {
            "id": candidate.get("id"),
            "name": candidate.get("name"),
            "party_id": party_id,
            "party_name": party.get("name", "Independent") if party else "Independent",
            "party_short_name": party.get("short_name", "IND") if party else "IND",
            "party_symbol": party.get("symbol", "") if party else "",
            "constituency_id": const_id,
            "constituency_name": constituency.get("name", "Unknown") if constituency else "Unknown",
            "constituency_state_id": constituency.get("state_id", "") if constituency else candidate.get("state_id", ""),
            "state_id": candidate.get("state_id", ""),
            "status": candidate.get("status", ""),
            "type": candidate.get("type", "MP"),
            "image_url": candidate.get("image_url"),
            "election_id": election_id,
        }

        if include_details:
            result.update({
                "education_background": candidate.get("education_background"),
                "political_background": candidate.get("political_background"),
                "family_background": candidate.get("family_background"),
                "assets": candidate.get("assets"),
                "liabilities": candidate.get("liabilities"),
                "crime_cases": candidate.get("crime_cases"),
            })

        return result

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._elections_cache = None
        self._election_data_cache.clear()
        self._parties_cache.clear()
        self._constituencies_cache.clear()
        self._candidates_cache.clear()
        logger.info("JsonDataService cache cleared")

    def reload_election_data(self, election_id: str) -> None:
        """Reload data for a specific election from disk."""
        self._parties_cache.pop(election_id, None)
        self._constituencies_cache.pop(election_id, None)
        self._candidates_cache.pop(election_id, None)
        logger.info(f"Reloaded data for election: {election_id}")
