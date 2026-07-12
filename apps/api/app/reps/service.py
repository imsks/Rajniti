"""Reps facade.

Serves representative data. May enrich answers via the rag module (a legal
downward dependency: reps -> rag). Must NOT import the sibling `promises`
module — cross-module data flows as DTOs through a lower layer or the routes
layer.
"""

from __future__ import annotations

from app.rag import RagService
from app.reps.dto import Representative


class RepsService:
    def __init__(self, rag: RagService | None = None) -> None:
        self._rag = rag or RagService()

    def get_representative(self, rep_id: str) -> Representative:
        """Return a representative by id.

        Placeholder. Real data access (Supabase) is wired in during migration.
        """
        return Representative(
            id=rep_id,
            name="[stub] Representative",
            house="MP",
            constituency="[stub]",
        )
