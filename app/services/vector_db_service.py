"""
VectorDBService — service-layer wrapper around ``app.core.vector_db.VectorDB``.

Provides a simplified interface for semantic search over politician data stored
in the local ChromaDB collection.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class VectorDBService:
    """Service wrapper over the ChromaDB-backed VectorDB.

    Delegates all heavy lifting to :class:`app.core.vector_db.VectorDB` and
    normalises its raw query output into the flat dicts consumed by
    :class:`~app.services.questions_service.QuestionsService`.
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        collection_name: Optional[str] = None,
    ) -> None:
        from app.core.vector_db import VectorDB

        self._vdb = VectorDB(db_path=db_path, collection_name=collection_name)
        logger.info("VectorDBService ready (collection: %s)", self._vdb.collection_name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return number of documents in the collection."""
        return self._vdb.count()

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic search over politician documents.

        Returns a list of normalised result dicts with keys:
        ``id``, ``document``, ``metadata``, ``distance``.

        An empty list is returned if the query fails.
        """
        try:
            raw = self._vdb.query(query_text=query, n_results=n_results, where=where)
        except Exception as exc:
            logger.error("VectorDB query failed: %s", exc)
            return []

        def _normalize_first_list(key: str) -> List[Any]:
            """
            Safely extract the first inner list for a given key from the raw
            VectorDB response. Returns an empty list if the structure is
            missing, empty, or malformed.
            """
            value = raw.get(key) or [[]]
            if not isinstance(value, list) or not value:
                return []
            first = value[0]
            if isinstance(first, list):
                return first
            # If the first element is not a list, treat as malformed.
            return []

        ids = _normalize_first_list("ids")
        docs = _normalize_first_list("documents")
        metas = _normalize_first_list("metadatas")
        dists = _normalize_first_list("distances")

        results: List[Dict[str, Any]] = []
        for i, pid in enumerate(ids):
            results.append(
                {
                    "id": pid,
                    "document": docs[i] if i < len(docs) else "",
                    "metadata": metas[i] if i < len(metas) else {},
                    "distance": dists[i] if i < len(dists) else None,
                }
            )
        return results
