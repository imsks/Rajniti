"""
Database Data Service Implementation

Reads data from the database using SQLAlchemy models.
Works with both local PostgreSQL and Supabase.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import func

from app.database import get_db_session
from app.database.models import Candidate as DbCandidate
from app.database.models import Constituency as DbConstituency
from app.database.models import Election as DbElection
from app.database.models import Party as DbParty

from .data_service import DataService


class DbDataService(DataService):
    """Database-backed data service implementation"""

    def __init__(self):
        self._elections_cache = None

    def get_elections(self) -> List[Dict[str, Any]]:
        """Get all available elections from database"""
        if self._elections_cache is None:
            with get_db_session() as session:
                db_elections = DbElection.get_all(session, skip=0, limit=1000)
                self._elections_cache = [
                    {
                        "id": e.id,
                        "name": e.name,
                        "type": e.type,
                        "year": e.year,
                    }
                    for e in db_elections
                ]
        return self._elections_cache

    def get_election(self, election_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific election by ID from database"""
        with get_db_session() as session:
            db_election = DbElection.get_by_id(session, election_id)
            if db_election:
                return {
                    "id": db_election.id,
                    "name": db_election.name,
                    "type": db_election.type,
                    "year": db_election.year,
                }
        return None

    def get_candidates(self, election_id: str) -> List[Dict[str, Any]]:
        """Get all candidates for an election"""
        # Verify election exists
        election = self.get_election(election_id)
        if not election:
            return []

        with get_db_session() as session:
            db_candidates = DbCandidate.get_all(session, skip=0, limit=10000)
            
            if not db_candidates:
                return []
            
            # Batch load parties and constituencies to avoid N+1 queries
            party_ids = {c.party_id for c in db_candidates}
            constituency_ids = {c.constituency_id for c in db_candidates}
            
            # Load all parties and constituencies in one query each
            # Handle empty sets to avoid SQLAlchemy errors
            parties = {}
            if party_ids:
                parties = {
                    p.id: p 
                    for p in session.query(DbParty).filter(DbParty.id.in_(party_ids)).all()
                }
            
            constituencies = {}
            if constituency_ids:
                constituencies = {
                    c.id: c 
                    for c in session.query(DbConstituency)
                    .filter(DbConstituency.id.in_(constituency_ids))
                    .all()
                }
            
            # Convert to dict format for API compatibility using caches
            return [
                self._candidate_to_dict(c, session, election_id, parties, constituencies)
                for c in db_candidates
            ]

    def get_parties(self, election_id: str) -> List[Dict[str, Any]]:
        """Get all parties for an election"""
        # Verify election exists
        election = self.get_election(election_id)
        if not election:
            return []

        with get_db_session() as session:
            db_parties = DbParty.get_all(session, skip=0, limit=10000)
            # Convert to dictionaries
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "short_name": p.short_name,
                    "symbol": p.symbol,
                }
                for p in db_parties
            ]

    def get_constituencies(self, election_id: str) -> List[Dict[str, Any]]:
        """Get all constituencies for an election"""
        # Verify election exists
        election = self.get_election(election_id)
        if not election:
            return []

        with get_db_session() as session:
            db_constituencies = DbConstituency.get_all(session, skip=0, limit=10000)
            # Convert to dictionaries
            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "state_id": c.state_id,
                }
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
                return self._candidate_to_dict(db_candidate, session, election_id, include_details=True)
            return None

    def get_candidate_by_id_only(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific candidate without election_id (defaults to lok-sabha-2024)"""
        with get_db_session() as session:
            db_candidate = DbCandidate.get_by_id(session, candidate_id)
            if not db_candidate:
                return None
            
            election_id = "lok-sabha-2024"
            return self._candidate_to_dict(db_candidate, session, election_id, include_details=True)

    def get_party_by_name(self, party_name: str, election_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific party"""
        # Verify election exists
        election = self.get_election(election_id)
        if not election:
            return None

        with get_db_session() as session:
            db_party = DbParty.get_by_name(session, party_name)
            if db_party:
                return {
                    "id": db_party.id,
                    "name": db_party.name,
                    "short_name": db_party.short_name,
                    "symbol": db_party.symbol,
                }
            return None

    def get_constituency_by_id(
        self, constituency_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific constituency"""
        # Verify election exists
        election = self.get_election(election_id)
        if not election:
            return None
        with get_db_session() as session:
            db_constituency = DbConstituency.get_by_id(session, constituency_id)
            if db_constituency:
                return {
                    "id": db_constituency.id,
                    "name": db_constituency.name,
                    "state_id": db_constituency.state_id,
                }
            return None

    # ---- Enrichment & derived views (used by controllers) ----

    def enrich_candidate_data(
        self, candidate: Dict[str, Any], election_id: str
    ) -> Dict[str, Any]:
        """
        Enrich a candidate record for API responses.

        For the DB-backed service, candidates returned by `get_candidates()` are
        already enriched (party/constituency names). Controllers still call this
        method, so keep it as a safe no-op.
        """
        return candidate

    def get_state_name(self, state_id: str) -> str:
        """
        Resolve a state ID/code to a name.

        DB schema currently stores state_id codes but does not include a state
        mapping table. Return the code as a fallback.
        """
        return state_id

    def get_election_statistics(self, election_id: str) -> Dict[str, int]:
        """
        Get statistics for an election using efficient COUNT queries.
        This avoids fetching all records when we only need counts.
        """
        with get_db_session() as session:
            # Use COUNT queries instead of fetching all records
            total_candidates = session.query(func.count(DbCandidate.id)).scalar() or 0
            total_winners = (
                session.query(func.count(DbCandidate.id))
                .filter(DbCandidate.status == "WON")
                .scalar()
                or 0
            )
            total_parties = session.query(func.count(func.distinct(DbParty.id))).scalar() or 0
            total_constituencies = (
                session.query(func.count(func.distinct(DbConstituency.id))).scalar() or 0
            )

            return {
                "total_candidates": total_candidates,
                "total_parties": total_parties,
                "total_constituencies": total_constituencies,
                "total_winners": total_winners,
            }

    def get_party_seat_counts(self, election_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get party-wise seat counts using efficient SQL GROUP BY query.
        Returns top parties by seats won.
        """
        with get_db_session() as session:
            # Use SQL GROUP BY to count seats per party efficiently
            party_seats = (
                session.query(
                    DbCandidate.party_id,
                    func.count(DbCandidate.id).label("seats_won")
                )
                .filter(DbCandidate.status == "WON")
                .group_by(DbCandidate.party_id)
                .order_by(func.count(DbCandidate.id).desc())
                .limit(limit)
                .all()
            )
            
            # Get party details for the top parties
            party_ids = [party_id for party_id, _ in party_seats]
            parties = {}
            if party_ids:
                parties = {
                    p.id: p 
                    for p in session.query(DbParty).filter(DbParty.id.in_(party_ids)).all()
                }
            
            # Build result list
            result = []
            for party_id, seats_won in party_seats:
                party = parties.get(party_id)
                if party:
                    result.append({
                        "party_name": party.name,
                        "party_short_name": party.short_name,
                        "seats_won": seats_won,
                    })
                elif party_id == "UNKNOWN" or not party:
                    result.append({
                        "party_name": "INDEPENDENT",
                        "party_short_name": "IND",
                        "seats_won": seats_won,
                    })
            
            return result

    def _candidate_to_dict(
        self, candidate: DbCandidate, session, election_id: str, 
        party_cache: Optional[Dict[str, DbParty]] = None,
        constituency_cache: Optional[Dict[str, DbConstituency]] = None,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """
        Convert database candidate to dictionary format with enriched data.

        Args:
            candidate: Database candidate model
            session: Database session for fetching related data
            election_id: Election ID
            party_cache: Optional cache of parties to avoid N+1 queries
            constituency_cache: Optional cache of constituencies to avoid N+1 queries
            include_details: Whether to include detailed fields (education, political, etc.)

        Returns:
            Dictionary with candidate data including party and constituency details
        """
        # Use cache if provided, otherwise fetch individually
        if party_cache is not None:
            party = party_cache.get(candidate.party_id)
        else:
            party = DbParty.get_by_id(session, candidate.party_id)
        
        party_name = party.name if party else "Unknown"
        party_short_name = party.short_name if party else "UNK"
        party_symbol = party.symbol if party else ""

        if constituency_cache is not None:
            constituency = constituency_cache.get(candidate.constituency_id)
        else:
            constituency = DbConstituency.get_by_id(session, candidate.constituency_id)
        
        constituency_name = constituency.name if constituency else "Unknown"
        constituency_state_id = constituency.state_id if constituency else ""

        result = {
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

        if include_details:
            result.update({
                "education_background": candidate.education_background,
                "political_background": candidate.political_background,
                "family_background": candidate.family_background,
                "assets": candidate.assets,
                "liabilities": candidate.liabilities,
                "crime_cases": candidate.crime_cases,
            })

        return result
