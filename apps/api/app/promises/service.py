"""Promises facade.

Serves promise data. May use the rag module to assess "made vs kept" evidence
(a legal downward dependency: promises -> rag). Must NOT import the sibling
`reps` module directly.
"""

from __future__ import annotations

from app.promises.dto import Promise
from app.rag import RagService


class PromisesService:
    def __init__(self, rag: RagService | None = None) -> None:
        self._rag = rag or RagService()

    def list_promises(self, representative_id: str) -> list[Promise]:
        """List promises for a representative.

        Placeholder. Real data access (Supabase) is wired in during migration.
        """
        return []
