"""
Election Controller

Handles business logic for election-related operations.
"""

from typing import Any, Dict, List, Optional

from app.services import data_service


class ElectionController:
    """Controller for election operations"""

    def __init__(self):
        self.data_service = data_service

    def get_all_elections(self) -> List[Dict[str, Any]]:
        """Get all elections with basic statistics"""
        elections = self.data_service.get_elections()
        result = []

        for election in elections:
            election_data = election.dict()

            # Add basic statistics
            candidates = self.data_service.get_candidates(election.id)
            parties = self.data_service.get_parties(election.id)
            constituencies = self.data_service.get_constituencies(election.id)

            # Count winners
            winners_count = sum(
                1 for c in candidates if c.get("status") == "WON"
            )

            election_data["statistics"] = {
                "total_candidates": len(candidates),
                "total_parties": len(parties),
                "total_constituencies": len(constituencies),
                "total_winners": winners_count,
            }

            result.append(election_data)

        return result

    def get_election_by_id(self, election_id: str) -> Optional[Dict[str, Any]]:
        """Get election details with comprehensive statistics"""
        election = self.data_service.get_election(election_id)
        if not election:
            return None

        result = election.dict()

        # Get detailed statistics
        candidates = self.data_service.get_candidates(election_id)
        parties = self.data_service.get_parties(election_id)
        constituencies = self.data_service.get_constituencies(election_id)

        # Count winners and party-wise seats
        winners_count = 0
        party_seats = {}

        for candidate in candidates:
            if candidate.get("status") == "WON":
                winners_count += 1
                
                # Count seats by party
                party_id = candidate.get("party_id", "UNKNOWN")
                party_seats[party_id] = party_seats.get(party_id, 0) + 1

        # Get top parties
        parties_by_id = {p.id: p for p in parties}
        top_parties = []
        for party_id, seats in sorted(
            party_seats.items(), key=lambda x: x[1], reverse=True
        )[:5]:
            party = parties_by_id.get(party_id)
            if party:
                top_parties.append({
                    "party_name": party.name,
                    "party_short_name": party.short_name,
                    "seats_won": seats,
                })
            elif party_id == "UNKNOWN":
                top_parties.append({
                    "party_name": "INDEPENDENT",
                    "party_short_name": "IND",
                    "seats_won": seats,
                })

        result["statistics"] = {
            "total_candidates": len(candidates),
            "total_parties": len(parties),
            "total_constituencies": len(constituencies),
            "total_winners": winners_count,
            "top_parties": top_parties,
        }

        return result
