"""
Vector Database Pipeline Service

Pipeline for syncing candidate data from JSON datasets to ChromaDB.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.services.vector_db_service import VectorDBService

logger = logging.getLogger(__name__)


class VectorDBPipeline:
    """
    Pipeline for syncing candidate data from JSON datasets to ChromaDB.

    This pipeline:
    1. Reads candidates from JSON files
    2. Converts candidate information to searchable text format
    3. Stores the text and metadata in ChromaDB for semantic search
    """

    def __init__(
        self, vector_db_service: Optional[VectorDBService] = None, data_dir: Optional[Path] = None
    ):
        self.vector_db = vector_db_service or VectorDBService(collection_name="candidates")
        self._data_dir = Path(data_dir) if data_dir is not None else Path(__file__).parent.parent / "data"
        logger.info("VectorDBPipeline initialized successfully")

    def _get_election_data_dir(self, election_id: str) -> Optional[Path]:
        lok = self._data_dir / "lok_sabha" / election_id
        if lok.exists():
            return lok

        vs = self._data_dir / "vidhan_sabha" / election_id
        if vs.exists():
            return vs

        vs_root = self._data_dir / "vidhan_sabha"
        if vs_root.exists():
            for d in vs_root.glob("*"):
                if d.is_dir() and election_id in d.name:
                    return d

        return None

    def _load_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        if not file_path.exists():
            return []
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [x for x in data if isinstance(x, dict)]
            if isinstance(data, dict):
                return [data]
            return []
        except Exception as e:
            logger.warning("Failed to read JSON %s: %s", file_path, e)
            return []

    def _load_candidates(self, election_id: str) -> List[Dict[str, Any]]:
        data_dir = self._get_election_data_dir(election_id)
        if not data_dir:
            return []
        candidates = self._load_json_file(data_dir / "candidates.json")
        return [c for c in candidates if c.get("name") != "NOTA"]

    def _candidate_to_text(self, candidate: Dict[str, Any]) -> str:
        text_parts = [
            f"Name: {candidate.get('name')}",
            f"Constituency: {candidate.get('constituency_id')}",
            f"State: {candidate.get('state_id')}",
            f"Party: {candidate.get('party_id')}",
            f"Status: {candidate.get('status')}",
            f"Type: {candidate.get('type')}",
        ]

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

        political_background = candidate.get("political_background")
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

        assets = candidate.get("assets")
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

        liabilities = candidate.get("liabilities")
        if liabilities:
            total_liabilities = sum(l.get("amount", 0) for l in liabilities)
            if total_liabilities > 0:
                text_parts.append(f"Liabilities: Total ₹{total_liabilities:,.2f}")

        crime_cases = candidate.get("crime_cases")
        if crime_cases:
            crime_count = len(crime_cases)
            charges_framed = sum(1 for case in crime_cases if case.get("charges_framed"))
            crime_parts = [f"{crime_count} criminal case(s)"]
            if charges_framed > 0:
                crime_parts.append(f"{charges_framed} with charges framed")
            text_parts.append(f"Criminal Cases: {'; '.join(crime_parts)}")

        return ". ".join(text_parts) + "."

    def _candidate_to_metadata(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {
            "candidate_id": candidate.get("id", ""),
            "name": candidate.get("name", ""),
            "party_id": candidate.get("party_id", ""),
            "constituency_id": candidate.get("constituency_id", ""),
            "state_id": candidate.get("state_id", ""),
            "status": candidate.get("status", ""),
            "type": candidate.get("type", "MP"),
        }

        if candidate.get("image_url"):
            metadata["image_url"] = candidate["image_url"]

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
        try:
            text = self._candidate_to_text(candidate)
            metadata = self._candidate_to_metadata(candidate)
            self.vector_db.upsert_candidate_data(
                candidate_id=str(candidate.get("id")), text=text, metadata=metadata
            )
            return True
        except Exception as e:
            logger.error("Failed to sync candidate %s: %s", candidate.get("id"), e)
            return False

    def sync_candidates_batch(
        self,
        election_id: str,
        batch_size: int = 100,
        offset: int = 0,
        filter_criteria: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        candidates = self._load_candidates(election_id)

        if filter_criteria:
            if filter_criteria.get("status"):
                candidates = [c for c in candidates if c.get("status") == filter_criteria["status"]]
            if filter_criteria.get("state_id"):
                candidates = [c for c in candidates if c.get("state_id") == filter_criteria["state_id"]]
            if filter_criteria.get("type"):
                candidates = [c for c in candidates if c.get("type") == filter_criteria["type"]]

        candidates = candidates[offset : offset + batch_size]

        stats = {"total": len(candidates), "synced": 0, "failed": 0}
        for c in candidates:
            if self.sync_candidate(c):
                stats["synced"] += 1
            else:
                stats["failed"] += 1
        return stats

    def sync_all_candidates(
        self,
        election_id: str,
        batch_size: int = 100,
        filter_criteria: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        overall = {"total": 0, "synced": 0, "failed": 0, "batches": 0}
        offset = 0
        while True:
            batch = self.sync_candidates_batch(
                election_id=election_id,
                batch_size=batch_size,
                offset=offset,
                filter_criteria=filter_criteria,
            )
            if batch["total"] == 0:
                break
            overall["total"] += batch["total"]
            overall["synced"] += batch["synced"]
            overall["failed"] += batch["failed"]
            overall["batches"] += 1
            offset += batch_size
        return overall

    def delete_candidate(self, candidate_id: str) -> bool:
        try:
            self.vector_db.delete_candidate(candidate_id)
            return True
        except Exception as e:
            logger.error("Failed to delete candidate %s: %s", candidate_id, e)
            return False

