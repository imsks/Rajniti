"""
Party Controller

Handles business logic for party-related operations.
"""

from typing import Any, Dict, Optional

from app.services import data_service


class PartyController:
    """Controller for party operations"""

    def __init__(self):
        self.data_service = data_service

    def get_parties_by_election(self, election_id: str) -> Optional[Dict[str, Any]]:
        """Get all parties for a specific election with seat counts"""
        election = self.data_service.get_election(election_id)
        if not election:
            return None

        parties = self.data_service.get_parties(election_id)
        candidates = self.data_service.get_candidates(election_id)

        # Count seats for each party
        party_seats = {}
        for candidate in candidates:
            if candidate.get("status") == "WON":
                party_id = candidate.get("party_id", "UNKNOWN")
                party_seats[party_id] = party_seats.get(party_id, 0) + 1

        # Prepare party data with seats
        parties_data = []
        for party in parties:
            party_dict = party.dict()
            party_dict["seats_won"] = party_seats.get(party.id, 0)
            parties_data.append(party_dict)

        # Sort by seats won
        parties_data.sort(key=lambda x: x["seats_won"], reverse=True)

        return {
            "election_id": election_id,
            "election_name": election.name,
            "total_parties": len(parties_data),
            "parties": parties_data,
        }

    def get_party_by_name(
        self, party_name: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific party details with candidate list"""
        party = self.data_service.get_party_by_name(party_name, election_id)
        if not party:
            return None

        # Get all candidates from this party
        candidates = self.data_service.get_candidates(election_id)
        party_candidates = []
        winners = 0

        for candidate in candidates:
            enriched = self.data_service.enrich_candidate_data(candidate, election_id)
            if (
                enriched.get("party_name", "").lower() == party.name.lower()
                or enriched.get("party_id") == party.id
            ):
                party_candidates.append(enriched)
                if candidate.get("status") == "WON":
                    winners += 1

        return {
            "election_id": election_id,
            "party": party.dict(),
            "seats_won": winners,
            "total_candidates": len(party_candidates),
            "candidates": party_candidates,
        }

    def get_party_performance(
        self, party_name: str, election_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get party performance with detailed statistics"""
        if not election_id:
            election_id = "lok-sabha-2024"

        election = self.data_service.get_election(election_id)
        if not election:
            return {"party_name": party_name, "performance": None}

        # Get party info
        party = self.data_service.get_party_by_name(party_name, election_id)
        if not party:
            return {"party_name": party_name, "performance": None}

        # Get candidates from this party
        candidates = self.data_service.get_candidates(election_id)
        party_candidates = []
        winners = 0
        state_wise_performance = {}

        for candidate in candidates:
            enriched = self.data_service.enrich_candidate_data(candidate, election_id)
            if (
                enriched.get("party_name", "").lower() == party.name.lower()
                or enriched.get("party_id") == party.id
            ):
                party_candidates.append(enriched)

                # Count winners
                if candidate.get("status") == "WON":
                    winners += 1

                # State-wise performance
                state_name = enriched.get("state_name", "Unknown")
                if state_name not in state_wise_performance:
                    state_wise_performance[state_name] = {
                        "total_candidates": 0,
                        "seats_won": 0,
                    }
                state_wise_performance[state_name]["total_candidates"] += 1
                if candidate.get("status") == "WON":
                    state_wise_performance[state_name]["seats_won"] += 1

        # Convert state-wise performance to list
        state_performance = [
            {
                "state_name": state,
                "total_candidates": data["total_candidates"],
                "seats_won": data["seats_won"],
                "win_percentage": round(
                    (data["seats_won"] / data["total_candidates"] * 100), 2
                )
                if data["total_candidates"] > 0
                else 0,
            }
            for state, data in state_wise_performance.items()
        ]
        # Sort by seats won
        state_performance.sort(key=lambda x: x["seats_won"], reverse=True)

        return {
            "party_name": party.name,
            "party_short_name": party.short_name,
            "election_id": election_id,
            "election_name": election.name,
            "total_candidates": len(party_candidates),
            "seats_won": winners,
            "win_percentage": round((winners / len(party_candidates) * 100), 2)
            if party_candidates
            else 0,
            "state_wise_performance": state_performance,
        }

    def get_all_parties(self) -> Dict[str, Any]:
        """Get all parties across all elections"""
        all_parties_dict = {}

        for election in self.data_service.get_elections():
            parties = self.data_service.get_parties(election.id)
            candidates = self.data_service.get_candidates(election.id)

            # Count seats for each party
            party_seats = {}
            for candidate in candidates:
                if candidate.get("status") == "WON":
                    party_id = candidate.get("party_id", "UNKNOWN")
                    party_seats[party_id] = party_seats.get(party_id, 0) + 1

            for party in parties:
                party_name = party.name
                seats_won = party_seats.get(party.id, 0)

                if party_name not in all_parties_dict:
                    all_parties_dict[party_name] = {
                        "party_name": party_name,
                        "party_short_name": party.short_name,
                        "symbol": party.symbol,
                        "elections": [],
                        "total_seats": 0,
                    }

                all_parties_dict[party_name]["elections"].append(
                    {
                        "election_id": election.id,
                        "election_name": election.name,
                        "seats_won": seats_won,
                    }
                )
                all_parties_dict[party_name]["total_seats"] += seats_won

        # Convert to list and sort by total seats
        parties_list = list(all_parties_dict.values())
        parties_list.sort(key=lambda x: x["total_seats"], reverse=True)

        return {
            "total_unique_parties": len(parties_list),
            "parties": parties_list,
        }
