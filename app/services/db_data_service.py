"""
Database Data Service Implementation

Reads data from the database using SQLAlchemy models.
Works with both local PostgreSQL and Supabase.
"""

from typing import Any, Dict, List, Optional

from app.database import get_db_session
from app.database.models import Candidate as DbCandidate
from app.database.models import Constituency as DbConstituency
from app.database.models import Election as DbElection
from app.database.models import Party as DbParty
from app.models import Constituency, Election, ElectionType, Party

from .data_service import DataService


class DbDataService(DataService):
    """Database-backed data service implementation"""

    def __init__(self):
        self._elections_cache = None

    def get_elections(self) -> List[Election]:
        """Get all available elections from database"""
        if self._elections_cache is None:
            with get_db_session() as session:
                db_elections = DbElection.get_all(session, skip=0, limit=1000)
                self._elections_cache = [
                    Election(
                        id=e.id,
                        name=e.name,
                        type=ElectionType(e.type),
                        year=e.year,
                    )
                    for e in db_elections
                ]
        return self._elections_cache

    def get_election(self, election_id: str) -> Optional[Election]:
        """Get a specific election by ID from database"""
        with get_db_session() as session:
            db_election = DbElection.get_by_id(session, election_id)
            if db_election:
                return Election(
                    id=db_election.id,
                    name=db_election.name,
                    type=ElectionType(db_election.type),
                    year=db_election.year,
                )
        return None

    def get_candidates(self, election_id: str) -> List[Dict[str, Any]]:
        """Get all candidates for an election"""
        # Verify election exists
        election = self.get_election(election_id)
        if not election:
            return []

        with get_db_session() as session:
            db_candidates = DbCandidate.get_all(session, skip=0, limit=10000)
            # Convert to dict format for API compatibility
            return [self._candidate_to_dict(c, session, election_id) for c in db_candidates]

    def get_parties(self, election_id: str) -> List[Party]:
        """Get all parties for an election"""
        # Verify election exists
        election = self.get_election(election_id)
        if not election:
            return []

        with get_db_session() as session:
            db_parties = DbParty.get_all(session, skip=0, limit=10000)
            # Convert to Pydantic models
            return [
                Party(
                    id=p.id,
                    name=p.name,
                    short_name=p.short_name,
                    symbol=p.symbol,
                )
                for p in db_parties
            ]

    def get_constituencies(self, election_id: str) -> List[Constituency]:
        """Get all constituencies for an election"""
        # Verify election exists
        election = self.get_election(election_id)
        if not election:
            return []

        with get_db_session() as session:
            db_constituencies = DbConstituency.get_all(session, skip=0, limit=10000)
            # Convert to Pydantic models
            return [
                Constituency(
                    id=c.id,
                    name=c.name,
                    state_id=c.state_id,
                )
                for c in db_constituencies
            ]

    def search_candidates(
        self, query: str, election_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search candidates by name, party, or constituency"""
        # If election_id is provided, verify it exists
        if election_id:
            election = self.get_election(election_id)
            if not election:
                return []

        with get_db_session() as session:
            # Search by name
            db_candidates = DbCandidate.search_by_name(session, query)
            # Get all elections to determine election_id for each candidate
            # For now, we'll use the first election if election_id not provided
            if not election_id:
                elections = self.get_elections()
                election_id = elections[0].id if elections else None
                if not election_id:
                    return []
            
            return [
                self._candidate_to_dict(c, session, election_id)
                for c in db_candidates
            ]

    def get_candidate_by_id(
        self, candidate_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific candidate"""
        # Verify election exists
        election = self.get_election(election_id)
        if not election:
            return None

        with get_db_session() as session:
            db_candidate = DbCandidate.get_by_id(session, candidate_id)
            if db_candidate:
                return self._candidate_to_dict(db_candidate, session, election_id)
            return None

    def get_party_by_name(self, party_name: str, election_id: str) -> Optional[Party]:
        """Get a specific party"""
        # Verify election exists
        election = self.get_election(election_id)
        if not election:
            return None

        with get_db_session() as session:
            db_party = DbParty.get_by_name(session, party_name)
            if db_party:
                return Party(
                    id=db_party.id,
                    name=db_party.name,
                    short_name=db_party.short_name,
                    symbol=db_party.symbol,
                )
            return None

    def get_constituency_by_id(
        self, constituency_id: str, election_id: str
    ) -> Optional[Constituency]:
        """Get a specific constituency"""
        # Verify election exists
        election = self.get_election(election_id)
        if not election:
            return None

        with get_db_session() as session:
            db_constituency = DbConstituency.get_by_id(session, constituency_id)
            if db_constituency:
                return Constituency(
                    id=db_constituency.id,
                    name=db_constituency.name,
                    state_id=db_constituency.state_id,
                )
            return None

    def _candidate_to_dict(
        self, candidate: DbCandidate, session, election_id: str
    ) -> Dict[str, Any]:
        """
        Convert database candidate to dictionary format with enriched data.

        Args:
            candidate: Database candidate model
            session: Database session for fetching related data

        Returns:
            Dictionary with candidate data including party and constituency details
        """
        # Get party details
        party = DbParty.get_by_id(session, candidate.party_id)
        party_name = party.name if party else "Unknown"
        party_short_name = party.short_name if party else "UNK"
        party_symbol = party.symbol if party else ""

        # Get constituency details
        constituency = DbConstituency.get_by_id(session, candidate.constituency_id)
        constituency_name = constituency.name if constituency else "Unknown"
        constituency_state_id = constituency.state_id if constituency else ""

        return {
            "id": candidate.id,
            "name": candidate.name,
            "party_id": candidate.party_id,
            "party_name": party_name,
            "party_short_name": party_short_name,
            "party_symbol": party_symbol,
            "constituency_id": candidate.constituency_id,
            "constituency_name": constituency_name,
            "constituency_state_id": constituency_state_id,
            "state_id": candidate.state_id,
            "status": candidate.status,
            "type": candidate.type,
            "image_url": candidate.image_url,
            "election_id": election_id,
        }
