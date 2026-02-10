"""
Vector DB Service — CRUD for Politician documents in ChromaDB.

Designed for simplicity: each Politician becomes one document with its
key fields as searchable text and flat metadata for filtering.

Usage:
    from app.services.vector_db_service import VectorDBService

    vdb = VectorDBService()
    vdb.upsert(politician_dict)
    results = vdb.search("Modi BJP")
    vdb.delete("mp_2024_s24_51")
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class VectorDBService:
    """
    Plain CRUD wrapper around ChromaDB for Politician documents.

    Each politician is stored as:
      - **document**: human-readable text blob for embedding/search
      - **metadata**: flat key-value pairs for filtering
      - **id**: the politician's unique ID
    """

    def __init__(
        self,
        collection_name: str = "politicians",
        persist_path: Optional[str] = None,
    ) -> None:
        import chromadb

        if persist_path is None:
            persist_path = os.getenv(
                "CHROMA_DB_PATH",
                str(Path(__file__).resolve().parent.parent.parent / "chroma_db"),
            )

        os.makedirs(persist_path, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        logger.info(
            "VectorDB ready: collection='%s', path='%s', docs=%d",
            collection_name,
            persist_path,
            self.collection.count(),
        )

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def politician_to_document(p: Dict[str, Any]) -> str:
        """
        Convert a Politician dict to a searchable text document.

        This is what gets embedded — so include everything meaningful.
        """
        parts: List[str] = []

        parts.append(f"Name: {p.get('name', 'Unknown')}")
        parts.append(f"Type: {p.get('type', '')}")
        parts.append(f"State: {p.get('state', '')}")
        parts.append(f"Constituency: {p.get('constituency', '')}")

        # Elections / party
        bg = p.get("political_background") or {}
        for election in bg.get("elections", []):
            parts.append(
                f"Election: {election.get('year', '')} {election.get('type', '')} — "
                f"{election.get('party', '')} from {election.get('constituency', '')} "
                f"({election.get('status', '')})"
            )
        if bg.get("summary"):
            parts.append(f"Political Summary: {bg['summary']}")

        # Education
        edu = p.get("education")
        if edu:
            parts.append(f"Education: {edu.get('qualification', '')}")
            if edu.get("institution"):
                parts[-1] += f" from {edu['institution']}"

        # Family
        for fm in p.get("family_background") or []:
            parts.append(f"Family: {fm.get('name', '')} ({fm.get('relation', '')})")

        # Crime
        for cr in p.get("criminal_records") or []:
            parts.append(
                f"Criminal Record: {cr.get('name', '')} "
                f"(Type: {cr.get('type', 'N/A')}, Year: {cr.get('year', 'N/A')})"
            )

        # Notes
        if p.get("notes"):
            parts.append(f"Notes: {p['notes']}")

        return ". ".join(parts)

    @staticmethod
    def politician_to_metadata(p: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract flat metadata for ChromaDB filtering.

        ChromaDB metadata values must be str, int, float, or bool.
        """
        meta: Dict[str, str] = {
            "name": p.get("name", ""),
            "type": p.get("type", ""),
            "state": p.get("state", ""),
            "constituency": p.get("constituency", ""),
        }

        # Party from latest election
        bg = p.get("political_background") or {}
        elections = bg.get("elections", [])
        if elections:
            latest = elections[-1]
            meta["party"] = latest.get("party", "")
            meta["year"] = str(latest.get("year", ""))

        return meta

    # ── CRUD ──────────────────────────────────────────────────────────────

    def upsert(self, politician: Dict[str, Any]) -> None:
        """Insert or update a single politician document."""
        pid = politician.get("id", "")
        if not pid:
            logger.warning("Skipping politician without id: %s", politician.get("name"))
            return

        doc = self.politician_to_document(politician)
        meta = self.politician_to_metadata(politician)

        self.collection.upsert(documents=[doc], metadatas=[meta], ids=[pid])
        logger.debug("Upserted %s (%s)", pid, politician.get("name", ""))

    def upsert_batch(self, politicians: List[Dict[str, Any]]) -> int:
        """Bulk upsert. Returns count of successfully upserted docs."""
        ids, docs, metas = [], [], []
        for p in politicians:
            pid = p.get("id", "")
            if not pid:
                continue
            ids.append(pid)
            docs.append(self.politician_to_document(p))
            metas.append(self.politician_to_metadata(p))

        if not ids:
            return 0

        # ChromaDB batch limit is ~5461; chunk if needed
        chunk_size = 5000
        count = 0
        for i in range(0, len(ids), chunk_size):
            self.collection.upsert(
                ids=ids[i : i + chunk_size],
                documents=docs[i : i + chunk_size],
                metadatas=metas[i : i + chunk_size],
            )
            count += len(ids[i : i + chunk_size])

        logger.info("Upserted %d documents", count)
        return count

    def get(self, politician_id: str) -> Optional[Dict[str, Any]]:
        """Get a single document by ID."""
        try:
            result = self.collection.get(ids=[politician_id])
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "document": result["documents"][0] if result["documents"] else None,
                    "metadata": result["metadatas"][0] if result["metadatas"] else {},
                }
        except Exception as exc:
            logger.error("Error getting %s: %s", politician_id, exc)
        return None

    def delete(self, politician_id: str) -> bool:
        """Delete a single document by ID."""
        try:
            self.collection.delete(ids=[politician_id])
            logger.info("Deleted %s", politician_id)
            return True
        except Exception as exc:
            logger.error("Error deleting %s: %s", politician_id, exc)
            return False

    def search(
        self,
        query: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search over politician documents.

        Args:
            query: natural language query
            n_results: max results
            where: optional ChromaDB filter, e.g. {"type": "MP"}

        Returns:
            List of dicts with id, document, metadata, distance.
        """
        try:
            kwargs: Dict[str, Any] = {
                "query_texts": [query],
                "n_results": min(n_results, self.collection.count() or 1),
            }
            if where:
                kwargs["where"] = where

            raw = self.collection.query(**kwargs)
            results: List[Dict[str, Any]] = []
            if raw["documents"]:
                for i in range(len(raw["documents"][0])):
                    results.append({
                        "id": raw["ids"][0][i],
                        "document": raw["documents"][0][i],
                        "metadata": raw["metadatas"][0][i] if raw["metadatas"] else {},
                        "distance": raw["distances"][0][i] if raw["distances"] else None,
                    })
            return results
        except Exception as exc:
            logger.error("Search error: %s", exc)
            return []

    def count(self) -> int:
        """Total document count."""
        return self.collection.count()

    def reset(self) -> None:
        """Delete ALL documents in the collection (use with caution)."""
        name = self.collection.name
        self.client.delete_collection(name)
        self.collection = self.client.get_or_create_collection(name=name)
        logger.warning("Reset collection '%s' — all documents deleted", name)
