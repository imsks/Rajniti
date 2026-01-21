"""
Abstract Data Service Interface

This defines the contract for data access.
Implementations can use JSON, database, or any other storage mechanism.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DataService(ABC):
    """Abstract data service interface"""

    @abstractmethod
    def get_elections(self) -> List[Dict[str, Any]]:
        """Get all available elections"""

    @abstractmethod
    def get_election(self, election_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific election by ID"""

    @abstractmethod
    def get_candidates(self, election_id: str) -> List[Dict[str, Any]]:
        """Get all candidates for an election"""

    @abstractmethod
    def get_parties(self, election_id: str) -> List[Dict[str, Any]]:
        """Get all parties for an election"""

    @abstractmethod
    def get_constituencies(self, election_id: str) -> List[Dict[str, Any]]:
        """Get all constituencies for an election"""

    @abstractmethod
    def search_candidates(
        self, query: str, election_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search candidates by name, party, or constituency"""

    @abstractmethod
    def get_candidate_by_id(
        self, candidate_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific candidate"""

    @abstractmethod
    def get_candidate_by_id_only(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific candidate without election_id"""

    @abstractmethod
    def get_party_by_name(self, party_name: str, election_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific party"""

    @abstractmethod
    def get_constituency_by_id(
        self, constituency_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific constituency"""

    # ---- Enrichment & derived views (used by controllers) ----

    @abstractmethod
    def enrich_candidate_data(
        self, candidate: Dict[str, Any], election_id: str
    ) -> Dict[str, Any]:
        """Enrich a candidate record with party/constituency metadata."""

    @abstractmethod
    def get_state_name(self, state_id: str) -> str:
        """Resolve a state ID/code to a human-readable name."""

    @abstractmethod
    def get_election_statistics(self, election_id: str) -> Dict[str, int]:
        """Return basic election statistics (counts) for dashboards."""

    @abstractmethod
    def get_party_seat_counts(
        self, election_id: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Return top parties by seats won for an election."""
