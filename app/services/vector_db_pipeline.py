"""
Vector Database Pipeline Service

This service orchestrates the ingestion of candidate data into ChromaDB
for semantic search capabilities. It converts candidate information from
JSON files into text embeddings and stores them in the vector database.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.vector_db_service import VectorDBService

logger = logging.getLogger(__name__)


class VectorDBPipeline:
    """
    Pipeline for syncing candidate data from JSON files to ChromaDB.

    This pipeline:
    1. Reads candidates from JSON files
    2. Converts candidate information to searchable text format
    3. Stores the text and metadata in ChromaDB for semantic search
    """

    def __init__(
        self,
        vector_db_service: Optional[VectorDBService] = None,
        data_dir: Optional[Path] = None,
    ):
        """
        Initialize the VectorDB pipeline.

        Args:
            vector_db_service: Optional VectorDBService instance.
                             If not provided, a new instance will be created.
            data_dir: Base directory for data files. Defaults to app/data
        """
        self.vector_db = vector_db_service or VectorDBService(
            collection_name="candidates"
        )

        if data_dir is None:
            self._data_dir = Path(__file__).parent.parent / "data"
        else:
            self._data_dir = Path(data_dir)

        logger.info("VectorDBPipeline initialized successfully")

    def _get_election_data_dir(self, election_id: str) -> Optional[Path]:
        """Get the data directory for a specific election."""
        # Try lok_sabha first
        lok_sabha_dir = self._data_dir / "lok_sabha" / election_id
        if lok_sabha_dir.exists():
            return lok_sabha_dir

        # Try vidhan_sabha
        vidhan_sabha_dir = self._data_dir / "vidhan_sabha" / election_id
        if vidhan_sabha_dir.exists():
            return vidhan_sabha_dir

        # Check if it matches a vidhan sabha folder pattern
        for vs_dir in (self._data_dir / "vidhan_sabha").glob("*"):
            if vs_dir.is_dir() and election_id in vs_dir.name:
                return vs_dir

        return None

    def _load_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load data from a JSON file."""
        if not file_path.exists():
            logger.warning(f"JSON file not found: {file_path}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return []

    def _load_candidates(self, election_id: str) -> List[Dict[str, Any]]:
        """Load candidates from JSON file."""
        data_dir = self._get_election_data_dir(election_id)
        if not data_dir:
            logger.error(f"Election data directory not found: {election_id}")
            return []

        candidates_file = data_dir / "candidates.json"
        candidates = self._load_json_file(candidates_file)

        # Filter out NOTA entries
        return [c for c in candidates if c.get("name") != "NOTA"]

    def _candidate_to_text(self, candidate: Dict[str, Any]) -> str:
        """
        Convert candidate data to searchable text format.

        Args:
            candidate: Candidate dictionary

        Returns:
            String representation of candidate for embedding
        """
        text_parts = [
            f"Name: {candidate.get('name', 'Unknown')}",
            f"Constituency: {candidate.get('constituency_id', 'Unknown')}",
            f"State: {candidate.get('state_id', 'Unknown')}",
            f"Party: {candidate.get('party_id', 'Unknown')}",
            f"Status: {candidate.get('status', 'Unknown')}",
            f"Type: {candidate.get('type', 'MP')}",
        ]

        # Add education background
        education_background = candidate.get("education_background")
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

        # Add political background
        political_background = candidate.get("political_background")
        if political_background:
            pol_text = []
            for pol in political_background:
                pol_parts = []
                if pol.get("election_year"):
                    pol_parts.append(f"In {pol['election_year']}")
                if pol.get("result"):
                    pol_parts.append(f"{pol['result'].lower()}")
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

        # Add family background
        family_background = candidate.get("family_background")
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

        # Add assets summary
        assets = candidate.get("assets")
        if assets:
            total_assets = sum(asset.get("amount", 0) for asset in assets)
            asset_types = set(
                asset.get("type") for asset in assets if asset.get("type")
            )
            if total_assets > 0 or asset_types:
                asset_parts = []
                if total_assets > 0:
                    asset_parts.append(f"Total assets: ₹{total_assets:,.2f}")
                if asset_types:
                    asset_parts.append(f"Asset types: {', '.join(asset_types)}")
                text_parts.append(f"Assets: {'; '.join(asset_parts)}")

        # Add liabilities summary
        liabilities = candidate.get("liabilities")
        if liabilities:
            total_liabilities = sum(
                liability.get("amount", 0) for liability in liabilities
            )
            if total_liabilities > 0:
                text_parts.append(f"Liabilities: Total ₹{total_liabilities:,.2f}")

        # Add crime cases info
        crime_cases = candidate.get("crime_cases")
        if crime_cases:
            crime_count = len(crime_cases)
            charges_framed = sum(
                1 for case in crime_cases if case.get("charges_framed")
            )
            crime_parts = [f"{crime_count} criminal case(s)"]
            if charges_framed > 0:
                crime_parts.append(f"{charges_framed} with charges framed")
            text_parts.append(f"Criminal Cases: {'; '.join(crime_parts)}")

        return ". ".join(text_parts) + "."

    def _candidate_to_metadata(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from candidate for filtering and retrieval.

        Args:
            candidate: Candidate dictionary

        Returns:
            Dictionary of metadata
        """
        metadata = {
            "candidate_id": candidate.get("id", ""),
            "name": candidate.get("name", ""),
            "party_id": candidate.get("party_id", ""),
            "constituency_id": candidate.get("constituency_id", ""),
            "state_id": candidate.get("state_id", ""),
            "status": candidate.get("status", ""),
            "type": candidate.get("type", "MP"),
        }

        # Add optional fields
        if candidate.get("image_url"):
            metadata["image_url"] = candidate["image_url"]

        # Add counts for detailed data
        if candidate.get("education_background"):
            metadata["education_count"] = len(candidate["education_background"])
        if candidate.get("political_background"):
            metadata["political_history_count"] = len(candidate["political_background"])
        if candidate.get("family_background"):
            metadata["family_members_count"] = len(candidate["family_background"])
        if candidate.get("assets"):
            metadata["assets_count"] = len(candidate["assets"])
        if candidate.get("crime_cases"):
            metadata["crime_cases_count"] = len(candidate["crime_cases"])

        return metadata

    def sync_candidate(self, candidate: Dict[str, Any]) -> bool:
        """
        Sync a single candidate to the vector database.

        Args:
            candidate: Candidate dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            text = self._candidate_to_text(candidate)
            metadata = self._candidate_to_metadata(candidate)

            self.vector_db.upsert_candidate_data(
                candidate_id=candidate["id"], text=text, metadata=metadata
            )
            logger.info(
                f"Successfully synced candidate {candidate.get('name')} (ID: {candidate.get('id')})"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to sync candidate {candidate.get('id')}: {e}")
            return False

    def sync_candidates_batch(
        self,
        election_id: str,
        batch_size: int = 100,
        offset: int = 0,
        filter_criteria: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """
        Sync a batch of candidates to the vector database.

        Args:
            election_id: Election ID to sync
            batch_size: Number of candidates to process in one batch
            offset: Number of candidates to skip
            filter_criteria: Optional filtering criteria (e.g., {"status": "WON"})

        Returns:
            Statistics dictionary with 'total', 'synced', 'failed'
        """
        logger.info(f"Starting batch sync: election={election_id}, batch_size={batch_size}, offset={offset}")

        candidates = self._load_candidates(election_id)

        # Apply filters if provided
        if filter_criteria:
            if filter_criteria.get("status"):
                candidates = [c for c in candidates if c.get("status") == filter_criteria["status"]]
            if filter_criteria.get("state_id"):
                candidates = [c for c in candidates if c.get("state_id") == filter_criteria["state_id"]]
            if filter_criteria.get("type"):
                candidates = [c for c in candidates if c.get("type") == filter_criteria["type"]]

        # Apply offset and limit
        candidates = candidates[offset : offset + batch_size]

        stats = {"total": len(candidates), "synced": 0, "failed": 0}

        for candidate in candidates:
            if self.sync_candidate(candidate):
                stats["synced"] += 1
            else:
                stats["failed"] += 1

        logger.info(f"Batch sync completed: {stats}")
        return stats

    def sync_all_candidates(
        self,
        election_id: str,
        batch_size: int = 100,
        filter_criteria: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """
        Sync all candidates to the vector database in batches.

        Args:
            election_id: Election ID to sync
            batch_size: Number of candidates to process in one batch
            filter_criteria: Optional filtering criteria

        Returns:
            Overall statistics dictionary
        """
        logger.info(f"Starting full sync of all candidates for {election_id} to vector database")

        overall_stats = {"total": 0, "synced": 0, "failed": 0, "batches": 0}

        offset = 0
        while True:
            batch_stats = self.sync_candidates_batch(
                election_id,
                batch_size=batch_size,
                offset=offset,
                filter_criteria=filter_criteria,
            )

            if batch_stats["total"] == 0:
                break

            overall_stats["total"] += batch_stats["total"]
            overall_stats["synced"] += batch_stats["synced"]
            overall_stats["failed"] += batch_stats["failed"]
            overall_stats["batches"] += 1

            offset += batch_size

            logger.info(
                f"Progress: {overall_stats['synced']}/{overall_stats['total']} candidates synced"
            )

        logger.info(f"Full sync completed: {overall_stats}")
        return overall_stats

    def delete_candidate(self, candidate_id: str) -> bool:
        """
        Delete a candidate from the vector database.

        Args:
            candidate_id: Unique identifier for the candidate

        Returns:
            True if successful, False otherwise
        """
        try:
            self.vector_db.delete_candidate(candidate_id)
            logger.info(f"Deleted candidate {candidate_id} from vector database")
            return True
        except Exception as e:
            logger.error(f"Failed to delete candidate {candidate_id}: {e}")
            return False
