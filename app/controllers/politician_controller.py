"""
Politician Controller

Business logic for politician-related API operations.
All data flows through PoliticianService (reads mp.json / mla.json).
"""

from typing import Any, Dict, List, Optional

from app.services.politician_service import PoliticianService

# Singleton service instance
_service = PoliticianService()


class PoliticianController:
    """Controller for politician operations."""

    def __init__(self) -> None:
        self.service = _service

    # ── List / Search ─────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        election_type: Optional[str] = None,
        state: Optional[str] = None,
        party: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        results = self.service.search(
            query,
            election_type=election_type,  # type: ignore[arg-type]
            state=state,
            party=party,
            limit=limit,
        )
        return {
            "query": query,
            "total": len(results),
            "politicians": results,
        }

    def get_all(
        self,
        election_type: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        if election_type:
            data = self.service.get_all(election_type)[:limit]  # type: ignore[arg-type]
        else:
            data = self.service.get_all_politicians()[:limit]
        return {
            "total": len(data),
            "politicians": data,
        }

    def get_by_id(self, politician_id: str) -> Optional[Dict[str, Any]]:
        return self.service.get_by_id(politician_id)

    def get_by_slug(self, politician_slug: str) -> Optional[Dict[str, Any]]:
        return self.service.get_by_slug(politician_slug)

    # ── Filters ───────────────────────────────────────────────────────────

    def get_by_state(
        self, state: str, election_type: Optional[str] = None
    ) -> Dict[str, Any]:
        results = self.service.get_by_state(state, election_type=election_type)  # type: ignore[arg-type]
        return {
            "state": state,
            "total": len(results),
            "politicians": results,
        }

    def get_by_party(
        self, party: str, election_type: Optional[str] = None
    ) -> Dict[str, Any]:
        results = self.service.get_by_party(party, election_type=election_type)  # type: ignore[arg-type]
        return {
            "party": party,
            "total": len(results),
            "politicians": results,
        }

    # ── Aggregations ──────────────────────────────────────────────────────

    def get_states(self, election_type: Optional[str] = None) -> List[str]:
        return self.service.get_states(election_type=election_type)  # type: ignore[arg-type]

    def get_parties(self, election_type: Optional[str] = None) -> List[str]:
        return self.service.get_parties(election_type=election_type)  # type: ignore[arg-type]

    def get_stats(self, election_type: Optional[str] = None) -> Dict[str, Any]:
        return self.service.stats(election_type=election_type)  # type: ignore[arg-type]
