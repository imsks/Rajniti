"""
JSON-first Candidate Enrichment Agent

This agent enriches candidates stored in `candidates.json` by calling the LLM
once per candidate (batched fields), then:
- Writes the new detailed fields back into the same JSON record
- Upserts the candidate into ChromaDB immediately (so search never needs an LLM)

Designed for one-time local runs (safe to resume; supports caching).
"""

import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import ValidationError

from app.schemas.candidate_data import (
    AssetDetails,
    CrimeCaseDetails,
    EducationDetails,
    FamilyMember,
    LiabilityDetails,
    PoliticalHistory,
)
from app.services.llm_cache import get_cache
from app.services.llm_service import get_llm_service
from app.services.vector_db_pipeline import VectorDBPipeline

logger = logging.getLogger(__name__)


DetailedFieldMap = {
    "education": "education_background",
    "political": "political_background",
    "family": "family_background",
    "assets": "assets",
    "liabilities": "liabilities",
    "crime_cases": "crime_cases",
}


class JsonCandidateAgent:
    """
    Enrich candidates in a JSON dataset and sync into vector DB.

    This mirrors the DB-backed CandidateAgent, but works without SQLAlchemy.
    """

    def __init__(
        self,
        election_id: str = "lok-sabha-2024",
        base_data_dir: Optional[Path] = None,
        llm_provider: Optional[str] = None,
        enable_cache: bool = True,
        cache_ttl_hours: int = 24,
        enable_vector_db: bool = True,
    ):
        self.election_id = election_id
        self.base_data_dir = (
            base_data_dir
            if base_data_dir is not None
            else Path(__file__).resolve().parents[1] / "data"
        )

        self.election_dir = self._resolve_election_dir(election_id)
        if not self.election_dir:
            raise ValueError(
                f"Could not resolve election directory for '{election_id}' under {self.base_data_dir}"
            )

        self.candidates_path = self.election_dir / "candidates.json"
        self.parties_path = self.election_dir / "parties.json"
        self.constituencies_path = self.election_dir / "constituencies.json"

        self.search_service = get_llm_service(provider=llm_provider)
        self.cache = get_cache(ttl_hours=cache_ttl_hours) if enable_cache else None

        self.enable_vector_db = enable_vector_db
        self.vector_db_pipeline = None
        if enable_vector_db:
            try:
                self.vector_db_pipeline = VectorDBPipeline()
            except Exception as e:
                logger.warning("Vector DB pipeline init failed: %s", e)
                self.enable_vector_db = False

        self._parties_by_id = self._load_index(self.parties_path, key="id")
        self._constituencies_by_id = self._load_index(self.constituencies_path, key="id")

    def _resolve_election_dir(self, election_id: str) -> Optional[Path]:
        if not self.base_data_dir.exists():
            return None
        for candidates_file in self.base_data_dir.rglob("candidates.json"):
            if candidates_file.parent.name == election_id:
                return candidates_file.parent
        return None

    def _load_index(self, path: Path, key: str) -> Dict[str, Dict[str, Any]]:
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as f:
                items = json.load(f)
            if not isinstance(items, list):
                return {}
            out: Dict[str, Dict[str, Any]] = {}
            for item in items:
                if isinstance(item, dict) and item.get(key) is not None:
                    out[str(item[key])] = item
            return out
        except Exception:
            return {}

    def _is_missing(self, value: Any) -> bool:
        if value is None:
            return True
        if value == "null":
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        return False

    def load_candidates(self) -> List[Dict[str, Any]]:
        if not self.candidates_path.exists():
            raise FileNotFoundError(f"Missing {self.candidates_path}")
        with self.candidates_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"{self.candidates_path} must be a JSON array")
        return data

    def _atomic_write_candidates(self, candidates: List[Dict[str, Any]]) -> None:
        tmp_path = self.candidates_path.with_suffix(self.candidates_path.suffix + ".tmp")
        bak_path = self.candidates_path.with_suffix(self.candidates_path.suffix + ".bak")

        # One-time backup (first time we write)
        if not bak_path.exists():
            try:
                bak_path.write_bytes(self.candidates_path.read_bytes())
            except Exception as e:
                logger.warning("Failed creating backup %s: %s", bak_path, e)

        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
        tmp_path.replace(self.candidates_path)

    def find_candidates_needing_data(
        self, candidates: List[Dict[str, Any]], limit: int = 100
    ) -> List[int]:
        indices: List[int] = []
        for i, c in enumerate(candidates):
            if any(self._is_missing(c.get(field)) for field in DetailedFieldMap.values()):
                indices.append(i)
                if len(indices) >= limit:
                    break
        return indices

    def _create_batch_query(self, candidate: Dict[str, Any], data_types: List[str]) -> str:
        base_info = str(candidate.get("name", "")).strip()

        constituency_id = str(candidate.get("constituency_id", "")).strip()
        state_id = str(candidate.get("state_id", "")).strip()
        constituency = self._constituencies_by_id.get(constituency_id) or {}
        constituency_name = str(constituency.get("name", "")).strip()

        if constituency_name:
            base_info += f" (constituency: {constituency_name})"
        elif constituency_id:
            base_info += f" (constituency_id: {constituency_id})"
        if state_id:
            base_info += f" (state_id: {state_id})"

        formats = {
            "education": "[{'year': 'YYYY', 'college': '...', 'stream': '...', 'other_details': '...'}]",
            "political": "[{'party': '...', 'constituency': '...', 'election_year': 'YYYY', 'position': '...', 'result': 'WON/LOST'}]",
            "family": "[{'name': '...', 'profession': '...', 'relation': '...', 'age': '...'}]",
            "assets": "[{'type': 'CASH/BOND/LAND/EQUITY/AUTOMOBILE/JEWELRY/OTHER', 'amount': 1000.0, 'description': '...', 'owned_by': 'SELF/SPOUSE/DEPENDENT/HUF/OTHER'}]",
            "liabilities": "[{'type': 'LOAN/OTHER', 'amount': 1000.0, 'description': '...', 'owned_by': 'SELF/SPOUSE/DEPENDENT/HUF/OTHER'}]",
            "crime_cases": "[{'fir_no': '...', 'police_station': '...', 'sections_applied': ['...'], 'charges_framed': true/false, 'description': '...'}]",
        }

        descriptions = {
            "education": "education background",
            "political": "political history (all elections contested)",
            "family": "family background (family members)",
            "assets": "declared assets",
            "liabilities": "declared liabilities",
            "crime_cases": "criminal cases",
        }

        query_parts = []
        for dt in data_types:
            query_parts.append(
                f"{dt}: {descriptions.get(dt, '')}. Format: {formats.get(dt, '')}"
            )

        return (
            f"Provide the following information about Indian politician {base_info}:\n\n"
            + "\n".join(f"{i+1}. {part}" for i, part in enumerate(query_parts))
            + "\n\n"
            "Use reliable sources like MyNeta.info and official affidavits where possible. "
            "If information is not available for any section, return an empty list [] for that section. "
            "Return ONLY valid JSON (no markdown, no code blocks, no extra text). "
            "Return a JSON object with keys exactly: "
            + ", ".join(data_types)
            + "."
        )

    def _extract_json_from_response(self, response_text: str) -> Optional[Any]:
        try:
            match = re.search(r"```(?:json)?\s*(.*?)```", response_text, re.DOTALL)
            if match:
                response_text = match.group(1)

            response_text = response_text.strip()

            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                pass

            start_idx_dict = response_text.find("{")
            end_idx_dict = response_text.rfind("}")
            if start_idx_dict != -1 and end_idx_dict != -1:
                return json.loads(response_text[start_idx_dict : end_idx_dict + 1])

            return None
        except Exception:
            return None

    def _fetch_batch_data(
        self, candidate: Dict[str, Any], data_types: List[str]
    ) -> Dict[str, Optional[List[Dict[str, Any]]]]:
        query = self._create_batch_query(candidate, data_types)

        if self.cache:
            cached = self.cache.get(query)
            if cached:
                response_text = cached.get("answer", "") or ""
            else:
                result = self.search_service.search_india(query)
                if result.get("error"):
                    return {dt: None for dt in data_types}
                response_text = result.get("answer", "") or ""
                self.cache.set(query, result)
        else:
            result = self.search_service.search_india(query)
            if result.get("error"):
                return {dt: None for dt in data_types}
            response_text = result.get("answer", "") or ""

        parsed = self._extract_json_from_response(response_text)
        out: Dict[str, Optional[List[Dict[str, Any]]]] = {}
        for dt in data_types:
            if isinstance(parsed, dict):
                val = parsed.get(dt, [])
            else:
                val = None
            if isinstance(val, dict):
                out[dt] = [val]
            elif isinstance(val, list):
                out[dt] = val
            else:
                out[dt] = None
        return out

    def _validate_and_format_data(
        self, data_type: str, data: List[Dict[str, Any]], candidate_name: str
    ) -> Optional[List[Dict[str, Any]]]:
        schemas = {
            "education": EducationDetails,
            "political": PoliticalHistory,
            "family": FamilyMember,
            "assets": AssetDetails,
            "liabilities": LiabilityDetails,
            "crime_cases": CrimeCaseDetails,
        }
        schema = schemas.get(data_type)
        if not schema:
            return None

        validated: List[Dict[str, Any]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            try:
                validated.append(schema(**item).dict())
            except ValidationError as ve:
                logger.debug(
                    "Skipping invalid %s for %s: %s (%s)", data_type, candidate_name, item, ve
                )
        return validated

    def populate_candidate_data(
        self, candidate: Dict[str, Any], delay_between_requests: float = 0.5
    ) -> Dict[str, bool]:
        status = {k: False for k in DetailedFieldMap.keys()}

        fields_to_fetch: List[str] = []
        for data_type, field_name in DetailedFieldMap.items():
            if self._is_missing(candidate.get(field_name)):
                fields_to_fetch.append(data_type)
            else:
                status[data_type] = True

        if not fields_to_fetch:
            return status

        batch_results = self._fetch_batch_data(candidate, fields_to_fetch)

        for data_type in fields_to_fetch:
            field_name = DetailedFieldMap[data_type]
            raw = batch_results.get(data_type)

            # If model explicitly returns [], store [] to mark as attempted.
            if raw == []:
                candidate[field_name] = []
                status[data_type] = True
                continue

            if raw:
                validated = self._validate_and_format_data(
                    data_type, raw, str(candidate.get("name", ""))
                )
                if validated is not None:
                    candidate[field_name] = validated
                    status[data_type] = True
                else:
                    # Mark attempted, but no valid data
                    candidate[field_name] = []
                    status[data_type] = True
            else:
                candidate[field_name] = []
                status[data_type] = True

        time.sleep(delay_between_requests)

        # Always sync the latest candidate snapshot to vector DB.
        if self.enable_vector_db and self.vector_db_pipeline:
            self.vector_db_pipeline.sync_candidate_dict(candidate)

        return status

    def run(
        self,
        batch_size: int = 10,
        flush_every: int = 1,
        delay_between_candidates: float = 0.5,
        delay_between_requests: float = 0.5,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        candidates = self.load_candidates()
        indices = self.find_candidates_needing_data(candidates, limit=batch_size)

        stats = {"total_processed": 0, "successful": 0, "partial": 0, "failed": 0}
        updated_since_flush = 0

        for n, idx in enumerate(indices, 1):
            cand = candidates[idx]
            before = cand.copy()
            status = self.populate_candidate_data(cand, delay_between_requests=delay_between_requests)

            stats["total_processed"] += 1
            fields_populated = sum(1 for v in status.values() if v)
            if fields_populated == 6:
                stats["successful"] += 1
            elif fields_populated > 0:
                stats["partial"] += 1
            else:
                stats["failed"] += 1

            # Detect actual changes to avoid needless writes
            if cand != before:
                updated_since_flush += 1

            if not dry_run and updated_since_flush >= flush_every:
                self._atomic_write_candidates(candidates)
                updated_since_flush = 0

            if n < len(indices):
                time.sleep(delay_between_candidates)

        if not dry_run and updated_since_flush > 0:
            self._atomic_write_candidates(candidates)

        return stats

