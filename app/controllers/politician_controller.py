"""
Politician Controller

Business logic for politician-related API operations.
All data flows through PoliticianService (reads mp.json / mla.json).
"""

from typing import Any, Dict, List, Optional

from app.services.politician_service import (
    ElectionType,
    PoliticianService,
)

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
        election_type: Optional[ElectionType] = None,
        state: Optional[str] = None,
        party: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        results = self.service.search(
            query,
            election_type=election_type,
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
        election_type: Optional[ElectionType] = None,
        limit: int = 1000,
    ) -> Dict[str, Any]:
        if election_type:
            data = self.service.get_all(election_type)[:limit]
        else:
            data = self.service.get_all_politicians()
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
        self, state: str, election_type: Optional[ElectionType] = None
    ) -> Dict[str, Any]:
        results = self.service.get_by_state(state, election_type=election_type)
        return {
            "state": state,
            "total": len(results),
            "politicians": results,
        }

    def get_by_party(
        self, party: str, election_type: Optional[ElectionType] = None
    ) -> Dict[str, Any]:
        results = self.service.get_by_party(party, election_type=election_type)
        return {
            "party": party,
            "total": len(results),
            "politicians": results,
        }

    # ── Aggregations ──────────────────────────────────────────────────────

    def get_states(self, election_type: Optional[ElectionType] = None) -> List[str]:
        return self.service.get_states(election_type=election_type)

    def get_parties(self, election_type: Optional[ElectionType] = None) -> List[str]:
        return self.service.get_parties(election_type=election_type)

    def get_stats(self, election_type: Optional[ElectionType] = None) -> Dict[str, Any]:
        return self.service.stats(election_type=election_type)

    # ── Catalog (SEO) ─────────────────────────────────────────────────────

    def list_catalog(
        self,
        *,
        page: int = 1,
        per_page: int = 48,
        election_type: Optional[ElectionType] = None,
        state: Optional[str] = None,
        q: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self.service.list_catalog(
            page=page,
            per_page=per_page,
            election_type=election_type,
            state=state,
            q=q,
        )

    def sitemap_entries(self) -> Dict[str, Any]:
        entries = self.service.sitemap_entries()
        return {"entries": entries, "total": len(entries)}
