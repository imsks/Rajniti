"""
Vector Database Pipeline Service

This service orchestrates the ingestion of candidate data into ChromaDB
for semantic search capabilities. It converts candidate information from
the database into text embeddings and stores them in the vector database.
"""

import logging
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.database.models import Candidate
from app.services.vector_db_service import VectorDBService

logger = logging.getLogger(__name__)


class VectorDBPipeline:
    """
    Pipeline for syncing candidate data from the database to ChromaDB.

    This pipeline:
    1. Fetches candidates from the database
    2. Converts candidate information to searchable text format
    3. Stores the text and metadata in ChromaDB for semantic search

    Note: `sync_candidate()` also accepts a candidate dict to support JSON-first
    enrichment workflows (no DB required) via `sync_candidate_dict()`.
    """

    def __init__(self, vector_db_service: Optional[VectorDBService] = None):
        """
        Initialize the VectorDB pipeline.

        Args:
            vector_db_service: Optional VectorDBService instance.
                             If not provided, a new instance will be created.
        """
        self.vector_db = vector_db_service or VectorDBService(collection_name="candidates")
        logger.info("VectorDBPipeline initialized successfully")

    @staticmethod
    def _get(
        candidate: Union[Candidate, Dict[str, Any]], key: str, default: Any = None
    ) -> Any:
        """Read attribute from SQLAlchemy model or key from dict."""
        if isinstance(candidate, dict):
            return candidate.get(key, default)
        return getattr(candidate, key, default)

    def _candidate_to_text(self, candidate: Union[Candidate, Dict[str, Any]]) -> str:
        """Convert candidate data to searchable text format."""
        text_parts = [
            f"Name: {self._get(candidate, 'name')}",
            f"Constituency: {self._get(candidate, 'constituency_id')}",
            f"State: {self._get(candidate, 'state_id')}",
            f"Party: {self._get(candidate, 'party_id')}",
            f"Status: {self._get(candidate, 'status')}",
            f"Type: {self._get(candidate, 'type')}",
        ]

        # Education
        education_background = self._get(candidate, "education_background")
        if education_background:
            edu_text = []
            for edu in education_background:
                edu_parts = []
                if edu.get("year"):
                    edu_parts.append(f"graduated in {edu['year']}")
                if edu.get("stream"):
                    edu_parts.append(f"studied {edu['stream']}")
                if edu.get("college"):
                    edu_parts.append(f"from {edu['college']}")
                if edu.get("other_details"):
                    edu_parts.append(edu["other_details"])
                if edu_parts:
                    edu_text.append(" ".join(edu_parts))
            if edu_text:
                text_parts.append(f"Education: {'; '.join(edu_text)}")

        # Political history
        political_background = self._get(candidate, "political_background")
        if political_background:
            pol_text = []
            for pol in political_background:
                pol_parts = []
                if pol.get("election_year"):
                    pol_parts.append(f"In {pol['election_year']}")
                if pol.get("result"):
                    pol_parts.append(f"{str(pol['result']).lower()}")
                if pol.get("constituency"):
                    pol_parts.append(f"from {pol['constituency']}")
                if pol.get("party"):
                    pol_parts.append(f"with {pol['party']}")
                if pol.get("position"):
                    pol_parts.append(f"as {pol['position']}")
                if pol_parts:
                    pol_text.append(" ".join(pol_parts))
            if pol_text:
                text_parts.append(f"Political History: {'; '.join(pol_text)}")

        # Family
        family_background = self._get(candidate, "family_background")
        if family_background:
            fam_text = []
            for fam in family_background:
                fam_parts = []
                if fam.get("name"):
                    fam_parts.append(fam["name"])
                if fam.get("relation"):
                    fam_parts.append(f"({fam['relation']})")
                if fam.get("profession"):
                    fam_parts.append(f"is a {fam['profession']}")
                if fam_parts:
                    fam_text.append(" ".join(fam_parts))
            if fam_text:
                text_parts.append(f"Family: {'; '.join(fam_text)}")

        # Assets summary
        assets = self._get(candidate, "assets")
        if assets:
            total_assets = sum(asset.get("amount", 0) for asset in assets)
            asset_types = set(asset.get("type") for asset in assets if asset.get("type"))
            if total_assets > 0 or asset_types:
                asset_parts = []
                if total_assets > 0:
                    asset_parts.append(f"Total assets: ₹{total_assets:,.2f}")
                if asset_types:
                    asset_parts.append(f"Asset types: {', '.join(sorted(asset_types))}")
                text_parts.append(f"Assets: {'; '.join(asset_parts)}")

        # Liabilities summary
        liabilities = self._get(candidate, "liabilities")
        if liabilities:
            total_liabilities = sum(l.get("amount", 0) for l in liabilities)
            if total_liabilities > 0:
                text_parts.append(f"Liabilities: Total ₹{total_liabilities:,.2f}")

        # Crime cases
        crime_cases = self._get(candidate, "crime_cases")
        if crime_cases:
            crime_count = len(crime_cases)
            charges_framed = sum(1 for case in crime_cases if case.get("charges_framed"))
            crime_parts = [f"{crime_count} criminal case(s)"]
            if charges_framed > 0:
                crime_parts.append(f"{charges_framed} with charges framed")
            text_parts.append(f"Criminal Cases: {'; '.join(crime_parts)}")

        return ". ".join(text_parts) + "."

    def _candidate_to_metadata(self, candidate: Union[Candidate, Dict[str, Any]]) -> Dict[str, Any]:
        """Extract metadata from candidate for filtering and retrieval."""
        metadata: Dict[str, Any] = {
            "candidate_id": self._get(candidate, "id"),
            "name": self._get(candidate, "name"),
            "party_id": self._get(candidate, "party_id"),
            "constituency_id": self._get(candidate, "constituency_id"),
            "state_id": self._get(candidate, "state_id"),
            "status": self._get(candidate, "status"),
            "type": self._get(candidate, "type"),
        }

        image_url = self._get(candidate, "image_url")
        if image_url:
            metadata["image_url"] = image_url

        education_background = self._get(candidate, "education_background")
        if education_background:
            metadata["education_count"] = len(education_background)
        political_background = self._get(candidate, "political_background")
        if political_background:
            metadata["political_history_count"] = len(political_background)
        family_background = self._get(candidate, "family_background")
        if family_background:
            metadata["family_members_count"] = len(family_background)
        assets = self._get(candidate, "assets")
        if assets:
            metadata["assets_count"] = len(assets)
        crime_cases = self._get(candidate, "crime_cases")
        if crime_cases:
            metadata["crime_cases_count"] = len(crime_cases)

        return metadata

    def sync_candidate(self, candidate: Union[Candidate, Dict[str, Any]]) -> bool:
        """Sync a single candidate to the vector database."""
        try:
            candidate_id = str(self._get(candidate, "id"))
            text = self._candidate_to_text(candidate)
            metadata = self._candidate_to_metadata(candidate)
            self.vector_db.upsert_candidate_data(candidate_id=candidate_id, text=text, metadata=metadata)
            logger.info(
                "Successfully synced candidate %s (ID: %s)",
                self._get(candidate, "name"),
                self._get(candidate, "id"),
            )
            return True
        except Exception as e:
            logger.error("Failed to sync candidate %s: %s", self._get(candidate, "id"), e)
            return False

    def sync_candidate_dict(self, candidate: Dict[str, Any]) -> bool:
        """Convenience wrapper for syncing a candidate dict (JSON-backed pipelines)."""
        return self.sync_candidate(candidate)

    def sync_candidates_batch(
        self,
        session: Session,
        batch_size: int = 100,
        offset: int = 0,
        filter_criteria: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """Sync a batch of candidates to the vector database (DB-backed)."""
        query = session.query(Candidate)

        if filter_criteria:
            if filter_criteria.get("status"):
                query = query.filter(Candidate.status == filter_criteria["status"])
            if filter_criteria.get("state_id"):
                query = query.filter(Candidate.state_id == filter_criteria["state_id"])
            if filter_criteria.get("type"):
                query = query.filter(Candidate.type == filter_criteria["type"])

        candidates = query.offset(offset).limit(batch_size).all()
        stats = {"total": len(candidates), "synced": 0, "failed": 0}

        for candidate in candidates:
            if self.sync_candidate(candidate):
                stats["synced"] += 1
            else:
                stats["failed"] += 1

        return stats

    def sync_all_candidates(
        self,
        session: Session,
        batch_size: int = 100,
        filter_criteria: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """Sync all candidates to the vector database in batches (DB-backed)."""
        overall = {"total": 0, "synced": 0, "failed": 0, "batches": 0}
        offset = 0
        while True:
            batch_stats = self.sync_candidates_batch(
                session=session,
                batch_size=batch_size,
                offset=offset,
                filter_criteria=filter_criteria,
            )
            if batch_stats["total"] == 0:
                break
            overall["total"] += batch_stats["total"]
            overall["synced"] += batch_stats["synced"]
            overall["failed"] += batch_stats["failed"]
            overall["batches"] += 1
            offset += batch_size
        return overall

    def delete_candidate(self, candidate_id: str) -> bool:
        """Delete a candidate from the vector database."""
        try:
            self.vector_db.delete_candidate(candidate_id)
            return True
        except Exception as e:
            logger.error("Failed to delete candidate %s: %s", candidate_id, e)
            return False

