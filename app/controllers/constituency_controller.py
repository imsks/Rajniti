"""
Constituency Controller

Handles business logic for constituency-related operations.
"""

from typing import Any, Dict, Optional

from app.services import data_service


class ConstituencyController:
    """Controller for constituency operations"""

    def __init__(self):
        self.data_service = data_service

    def get_constituencies_by_election(
        self, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get all constituencies for a specific election"""
        election = self.data_service.get_election(election_id)
        if not election:
            return None

        constituencies = self.data_service.get_constituencies(election_id)

        # Enrich with state names
        constituencies_data = []
        for const in constituencies:
            const_dict = const.dict()
            const_dict["state_name"] = self.data_service.get_state_name(
                const.state_id
            )
            constituencies_data.append(const_dict)

        # Sort by state name and then constituency name
        constituencies_data.sort(
            key=lambda x: (x.get("state_name", ""), x.get("name", ""))
        )

        return {
            "election_id": election_id,
            "election_name": election.name,
            "total_constituencies": len(constituencies_data),
            "constituencies": constituencies_data,
        }

    def get_constituency_by_id(
        self, constituency_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific constituency details with candidates"""
        constituency = self.data_service.get_constituency_by_id(
            constituency_id, election_id
        )
        if not constituency:
            return None

        # Get candidates for this constituency
        candidates = self.data_service.get_candidates(election_id)
        constituency_candidates = []
        winner = None

        for candidate in candidates:
            if candidate.get("constituency_id") == constituency_id:
                enriched = self.data_service.enrich_candidate_data(
                    candidate, election_id
                )
                constituency_candidates.append(enriched)

                # Find winner
                if candidate.get("status") == "WON":
                    winner = enriched

        # Sort candidates by status (WON first)
        constituency_candidates.sort(
            key=lambda x: (x.get("status") != "WON", x.get("name", ""))
        )

        return {
            "constituency": {
                "id": constituency.id,
                "name": constituency.name,
                "state_id": constituency.state_id,
                "state_name": self.data_service.get_state_name(constituency.state_id),
            },
            "election_id": election_id,
            "total_candidates": len(constituency_candidates),
            "winner": winner,
            "all_candidates": constituency_candidates,
        }

    def get_constituencies_by_state(self, state_code: str) -> Dict[str, Any]:
        """Get all constituencies in a specific state"""
        results = []

        # Only lok-sabha-2024 for now
        election = self.data_service.get_election("lok-sabha-2024")
        if election:
            constituencies = self.data_service.get_constituencies(election.id)
            for const in constituencies:
                if const.state_id.upper() == state_code.upper():
                    const_data = const.dict()
                    const_data["state_name"] = self.data_service.get_state_name(
                        const.state_id
                    )
                    const_data["election_id"] = election.id
                    const_data["election_name"] = election.name
                    results.append(const_data)

        # Sort by constituency name
        results.sort(key=lambda x: x.get("name", ""))

        return {
            "state_code": state_code,
            "state_name": self.data_service.get_state_name(state_code),
            "total_constituencies": len(results),
            "constituencies": results,
        }

    def get_constituency_results(
        self, constituency_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed results for a constituency"""
        constituency_data = self.get_constituency_by_id(constituency_id, election_id)
        if not constituency_data:
            return None

        candidates = constituency_data["all_candidates"]

        # Calculate victory margin (difference between 1st and 2nd)
        victory_margin = 0
        if len(candidates) >= 2:
            # Candidates are already sorted with winner first
            victory_margin = 0  # Can calculate from vote data if available

        return {
            "constituency": constituency_data["constituency"],
            "election_id": election_id,
            "total_candidates": len(candidates),
            "victory_margin": victory_margin,
            "winner": constituency_data["winner"],
            "results": candidates,
        }
