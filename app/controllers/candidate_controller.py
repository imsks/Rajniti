"""
Candidate Controller

Handles business logic for candidate-related operations.
"""

from typing import Any, Dict, Optional

from app.services import data_service


class CandidateController:
    """Controller for candidate operations"""

    def __init__(self):
        self.data_service = data_service

    def search_candidates(
        self, query: str, election_id: Optional[str] = None, limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search candidates across elections"""
        # Default to lok-sabha-2024 if no election_id provided
        if not election_id:
            election_id = "lok-sabha-2024"

        results = self.data_service.search_candidates(query, election_id)

        if limit:
            results = results[:limit]

        return {
            "query": query,
            "election_id": election_id,
            "total_results": len(results),
            "candidates": results,
        }

    def get_candidates_by_election(
        self, election_id: str, limit: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get all candidates for a specific election"""
        election = self.data_service.get_election(election_id)
        if not election:
            return None

        candidates = self.data_service.get_candidates(election_id)

        # Enrich all candidates
        enriched_candidates = [
            self.data_service.enrich_candidate_data(candidate, election_id)
            for candidate in candidates
        ]

        if limit:
            enriched_candidates = enriched_candidates[:limit]

        return {
            "election_id": election_id,
            "election_name": election.name,
            "total_candidates": len(candidates),
            "showing": len(enriched_candidates),
            "candidates": enriched_candidates,
        }

    def get_candidate_by_id(
        self, candidate_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific candidate details with full information"""
        candidate = self.data_service.get_candidate_by_id(candidate_id, election_id)
        return candidate

    def get_candidates_by_party(
        self, party_name: str, election_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all candidates from a specific party"""
        if not election_id:
            election_id = "lok-sabha-2024"

        election = self.data_service.get_election(election_id)
        if not election:
            return {
                "party_name": party_name,
                "election_id": election_id,
                "total_candidates": 0,
                "candidates": [],
            }

        candidates = self.data_service.get_candidates(election_id)
        results = []

        for candidate in candidates:
            enriched = self.data_service.enrich_candidate_data(candidate, election_id)
            # Match by party name or short name
            if (
                enriched.get("party_name", "").lower() == party_name.lower()
                or enriched.get("party_short_name", "").lower() == party_name.lower()
            ):
                results.append(enriched)

        return {
            "party_name": party_name,
            "election_id": election_id,
            "total_candidates": len(results),
            "candidates": results,
        }

    def get_candidates_by_constituency(
        self, constituency_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get all candidates from a specific constituency"""
        election = self.data_service.get_election(election_id)
        if not election:
            return None

        # Get constituency details
        constituency = self.data_service.get_constituency_by_id(
            constituency_id, election_id
        )
        if not constituency:
            return None

        candidates = self.data_service.get_candidates(election_id)
        constituency_candidates = []

        for candidate in candidates:
            if candidate.get("constituency_id") == constituency_id:
                enriched = self.data_service.enrich_candidate_data(
                    candidate, election_id
                )
                constituency_candidates.append(enriched)

        # Sort by status (WON first) and then by name
        constituency_candidates.sort(
            key=lambda x: (x.get("status") != "WON", x.get("name", ""))
        )

        return {
            "constituency_id": constituency_id,
            "constituency_name": constituency.name,
            "state_id": constituency.state_id,
            "state_name": self.data_service.get_state_name(constituency.state_id),
            "election_id": election_id,
            "total_candidates": len(constituency_candidates),
            "candidates": constituency_candidates,
        }

    def get_winning_candidates(
        self, election_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all winning candidates"""
        if not election_id:
            election_id = "lok-sabha-2024"

        election = self.data_service.get_election(election_id)
        if not election:
            return {
                "election_id": election_id,
                "total_winners": 0,
                "winners": [],
            }

        candidates = self.data_service.get_candidates(election_id)
        results = []

        for candidate in candidates:
            if candidate.get("status") == "WON":
                enriched = self.data_service.enrich_candidate_data(
                    candidate, election_id
                )
                results.append(enriched)

        return {
            "election_id": election_id,
            "election_name": election.name,
            "total_winners": len(results),
            "winners": results,
        }
