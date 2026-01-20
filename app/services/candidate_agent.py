"""
Candidate Data Population Agent

This agent fetches detailed information for candidates using LLM and:
1. Reads candidates from JSON files
2. Writes enriched data back to JSON files
3. Syncs to ChromaDB for vector search

Optimizations:
- Batch queries: Combines multiple data requests into single API call
- Caching: Avoids redundant API calls for similar queries
- Multi-provider support: Can use Perplexity, OpenAI, or Anthropic
- Incremental saves: Progress is saved after each candidate
"""

import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

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


class CandidateAgent:
    """
    Agent for populating candidate detailed information from JSON files.

    Key features:
    - Reads/writes to JSON files (no database dependency)
    - Batch queries: Combines multiple data requests into single API call
    - Caching: Avoids redundant API calls
    - Multi-provider support: Perplexity, OpenAI, or Anthropic
    - Syncs to ChromaDB for vector search
    """

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        enable_cache: bool = True,
        cache_ttl_hours: int = 24,
        enable_vector_db: bool = True,
        data_dir: Optional[Path] = None,
    ):
        """
        Initialize the candidate data agent.

        Args:
            llm_provider: LLM provider name ('perplexity', 'openai', 'anthropic').
                         If None, reads from LLM_PROVIDER env var
            enable_cache: Whether to enable response caching
            cache_ttl_hours: Cache TTL in hours
            enable_vector_db: Whether to automatically sync to vector DB
            data_dir: Base directory for data files. Defaults to app/data
        """
        # Initialize LLM service
        self.search_service = get_llm_service(provider=llm_provider)
        logger.info(f"Using LLM provider: {llm_provider or 'default'}")

        # Initialize cache
        self.cache = get_cache(ttl_hours=cache_ttl_hours) if enable_cache else None
        if enable_cache:
            logger.info(f"Response caching enabled (TTL: {cache_ttl_hours} hours)")

        # Data directory
        if data_dir is None:
            self._data_dir = Path(__file__).parent.parent / "data"
        else:
            self._data_dir = Path(data_dir)

        self.enable_vector_db = enable_vector_db
        self.vector_db_pipeline = None

        if enable_vector_db:
            try:
                self.vector_db_pipeline = VectorDBPipeline()
                logger.info("Vector DB pipeline initialized for automatic sync")
            except Exception as e:
                logger.warning(f"Failed to initialize vector DB pipeline: {e}")
                logger.warning("Continuing without vector DB sync")
                self.enable_vector_db = False

        logger.info("CandidateAgent initialized successfully")

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

    def _load_candidates(self, election_id: str) -> List[Dict[str, Any]]:
        """Load candidates from JSON file."""
        data_dir = self._get_election_data_dir(election_id)
        if not data_dir:
            logger.error(f"Election data directory not found: {election_id}")
            return []

        candidates_file = data_dir / "candidates.json"
        if not candidates_file.exists():
            logger.error(f"Candidates file not found: {candidates_file}")
            return []

        try:
            with open(candidates_file, "r", encoding="utf-8") as f:
                candidates = json.load(f)
            # Filter out NOTA entries
            return [c for c in candidates if c.get("name") != "NOTA"]
        except Exception as e:
            logger.error(f"Failed to load candidates: {e}")
            return []

    def _save_candidates(
        self, election_id: str, candidates: List[Dict[str, Any]]
    ) -> bool:
        """Save candidates to JSON file with backup."""
        data_dir = self._get_election_data_dir(election_id)
        if not data_dir:
            logger.error(f"Election data directory not found: {election_id}")
            return False

        candidates_file = data_dir / "candidates.json"
        backup_file = data_dir / "candidates.json.backup"

        try:
            # Create backup
            if candidates_file.exists():
                import shutil

                shutil.copy2(candidates_file, backup_file)

            # Write new data
            with open(candidates_file, "w", encoding="utf-8") as f:
                json.dump(candidates, f, ensure_ascii=False, indent=4)

            logger.info(f"Saved {len(candidates)} candidates to {candidates_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save candidates: {e}")
            # Restore backup if available
            if backup_file.exists():
                import shutil

                shutil.copy2(backup_file, candidates_file)
                logger.info("Restored from backup")
            return False

    def find_candidates_needing_data(
        self, election_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find candidates that are missing detailed information.

        Args:
            election_id: Election ID to search in
            limit: Maximum number of candidates to return

        Returns:
            List of candidate dictionaries that need data population
        """
        logger.info(f"Finding candidates needing data (limit: {limit})")

        candidates = self._load_candidates(election_id)
        candidates_needing_data = []

        for candidate in candidates:
            # Check if any detailed field is missing
            if (
                not candidate.get("education_background")
                or not candidate.get("political_background")
                or not candidate.get("family_background")
                or not candidate.get("assets")
                or not candidate.get("liabilities")
                or not candidate.get("crime_cases")
            ):
                candidates_needing_data.append(candidate)
                if len(candidates_needing_data) >= limit:
                    break

        logger.info(f"Found {len(candidates_needing_data)} candidates needing data")
        return candidates_needing_data

    def _create_batch_query(
        self, candidate: Dict[str, Any], data_types: List[str]
    ) -> str:
        """
        Create a single batch query for multiple data types.

        This is the KEY OPTIMIZATION: Instead of 6 separate API calls,
        we combine them into one.
        """
        base_info = f"{candidate['name']}"
        if candidate.get("constituency_id"):
            base_info += f" from constituency {candidate['constituency_id']}"

        query_parts = []
        formats = {
            "education": "[{'year': '...', 'college': '...', 'stream': '...', 'other_details': '...'}]",
            "political": "[{'party': '...', 'constituency': '...', 'election_year': '...', 'position': '...', 'result': 'WON/LOST'}]",
            "family": "[{'name': '...', 'profession': '...', 'relation': '...', 'age': '...'}]",
            "assets": "[{'type': '...', 'amount': 1000.0, 'description': '...', 'owned_by': '...'}]",
            "liabilities": "[{'type': '...', 'amount': 1000.0, 'description': '...', 'owned_by': '...'}]",
            "crime_cases": "[{'fir_no': '...', 'police_station': '...', 'sections_applied': ['...'], 'charges_framed': true/false, 'description': '...'}]",
        }

        descriptions = {
            "education": "education background with year, college, stream, and other details",
            "political": "political history with all elections contested (party, constituency, election_year, position, result)",
            "family": "family background with family members (name, profession, relation, age)",
            "assets": "declared assets (type: CASH/BOND/LAND/EQUITY/AUTOMOBILE/JEWELRY/OTHER, amount, description, owned_by)",
            "liabilities": "declared liabilities (type: LOAN/OTHER, amount, description, owned_by)",
            "crime_cases": "criminal cases (FIR No, Police Station, Sections Applied, Charges Framed, description)",
        }

        for data_type in data_types:
            desc = descriptions.get(data_type, "")
            fmt = formats.get(data_type, "")
            query_parts.append(f"{data_type.capitalize()}: {desc}. Format: {fmt}")

        combined_query = (
            f"Provide the following information about Indian politician {base_info}:\n\n"
            + "\n".join(f"{i+1}. {part}" for i, part in enumerate(query_parts))
            + "\n\n"
            "Search for this information using reliable sources like MyNeta.info. "
            "If information is not available for any section, return an empty list [] for that section. "
            "Return ONLY valid JSON objects, no markdown formatting, no code blocks, no other text. "
            "Do not include source citations or 'According to...' phrases in the values. "
            "Format the response as a JSON object with keys matching the data types above, "
            "each containing an array of objects."
        )

        return combined_query

    def _extract_json_from_response(self, response_text: str) -> Optional[Any]:
        """Extract JSON data from LLM response."""
        try:
            # Remove markdown code blocks if present
            match = re.search(r"```(?:json)?\s*(.*?)```", response_text, re.DOTALL)
            if match:
                response_text = match.group(1)

            response_text = response_text.strip()

            # Try to parse directly
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                pass

            # Fallback: find array or object
            start_idx_list = response_text.find("[")
            end_idx_list = response_text.rfind("]")
            start_idx_dict = response_text.find("{")
            end_idx_dict = response_text.rfind("}")

            if start_idx_list != -1 and end_idx_list != -1:
                if start_idx_dict == -1 or start_idx_list < start_idx_dict:
                    json_str = response_text[start_idx_list : end_idx_list + 1]
                    return json.loads(json_str)

            if start_idx_dict != -1 and end_idx_dict != -1:
                json_str = response_text[start_idx_dict : end_idx_dict + 1]
                return json.loads(json_str)

            return None
        except Exception as e:
            logger.warning(f"Failed to parse JSON from response: {e}")
            logger.debug(f"Raw response: {response_text[:200]}...")
            return None

    def _fetch_batch_data(
        self, candidate: Dict[str, Any], data_types: List[str]
    ) -> Dict[str, Optional[List[Dict[str, Any]]]]:
        """
        Fetch multiple data types in a single API call.

        This is the main optimization - reduces 6 API calls to 1.
        """
        query = self._create_batch_query(candidate, data_types)

        # Check cache first
        if self.cache:
            cached = self.cache.get(query)
            if cached:
                logger.info(f"Using cached response for {candidate['name']}")
                response_text = cached.get("answer", "")
            else:
                result = self.search_service.search_india(query)
                if result.get("error"):
                    logger.error(f"LLM error: {result['error']}")
                    return {dt: None for dt in data_types}
                response_text = result.get("answer", "")
                # Cache the response
                self.cache.set(query, result)
        else:
            result = self.search_service.search_india(query)
            if result.get("error"):
                logger.error(f"LLM error: {result['error']}")
                return {dt: None for dt in data_types}
            response_text = result.get("answer", "")

        # Parse the combined response
        parsed = self._extract_json_from_response(response_text)

        results = {}
        for data_type in data_types:
            if isinstance(parsed, dict):
                # Response is a dict with keys matching data_types
                data = parsed.get(data_type, [])
            elif isinstance(parsed, list) and len(parsed) == len(data_types):
                # Response is a list in the same order as data_types
                idx = data_types.index(data_type)
                data = parsed[idx] if idx < len(parsed) else []
            else:
                # Fallback: try to extract from text
                data = None

            if data is None or (isinstance(data, list) and len(data) == 0):
                results[data_type] = None
            else:
                if isinstance(data, dict):
                    data = [data]
                results[data_type] = data

        return results

    def _validate_and_format_data(
        self,
        data_type: str,
        data: List[Dict[str, Any]],
        candidate_name: str,
    ) -> Optional[List[Dict[str, Any]]]:
        """Validate and format data using Pydantic schemas."""
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

        validated_data = []
        for item in data:
            try:
                validated_data.append(schema(**item).dict())
            except ValidationError as ve:
                logger.warning(
                    f"Skipping invalid {data_type} data for {candidate_name} - {item}: {ve}"
                )

        if validated_data:
            logger.info(
                f"✅ {data_type.capitalize()} data found for {candidate_name} ({len(validated_data)} records)"
            )
            return validated_data
        return None

    def populate_candidate_data(
        self,
        candidate: Dict[str, Any],
        election_id: str,
        delay_between_requests: float = 1.0,
    ) -> Dict[str, bool]:
        """
        Populate all missing data fields for a candidate using batch queries.

        Args:
            candidate: Candidate dictionary to populate
            election_id: Election ID for saving
            delay_between_requests: Delay in seconds

        Returns:
            Dictionary with status of each field update
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing candidate: {candidate['name']} (ID: {candidate['id']})")
        logger.info(f"{'='*60}\n")

        status = {
            "education": False,
            "political": False,
            "family": False,
            "assets": False,
            "liabilities": False,
            "crime_cases": False,
        }

        # Determine which fields need to be fetched
        fields_to_fetch = []
        field_mapping = {
            "education": "education_background",
            "political": "political_background",
            "family": "family_background",
            "assets": "assets",
            "liabilities": "liabilities",
            "crime_cases": "crime_cases",
        }

        for data_type, field_name in field_mapping.items():
            if not candidate.get(field_name):
                fields_to_fetch.append(data_type)
            else:
                logger.info(
                    f"⏭️  {data_type.capitalize()} data already exists for {candidate['name']}"
                )
                status[data_type] = True

        if not fields_to_fetch:
            logger.info(f"✅ All data already exists for {candidate['name']}")
            return status

        # Fetch all missing fields in a single batch query
        logger.info(
            f"Fetching {len(fields_to_fetch)} data types in batch: {', '.join(fields_to_fetch)}"
        )
        batch_results = self._fetch_batch_data(candidate, fields_to_fetch)

        # Validate and format each result
        for data_type in fields_to_fetch:
            data = batch_results.get(data_type)
            if data:
                validated = self._validate_and_format_data(
                    data_type, data, candidate["name"]
                )
                if validated:
                    field_name = field_mapping[data_type]
                    candidate[field_name] = validated
                    status[data_type] = True

        # Small delay before next candidate
        time.sleep(delay_between_requests)

        # Sync to vector DB if enabled
        if self.enable_vector_db and self.vector_db_pipeline:
            try:
                if self.vector_db_pipeline.sync_candidate(candidate):
                    logger.info(f"🔍 Synced {candidate['name']} to vector database")
                else:
                    logger.warning(
                        f"⚠️  Failed to sync {candidate['name']} to vector database"
                    )
            except Exception as ve:
                logger.warning(f"⚠️  Vector DB sync error for {candidate['name']}: {ve}")

        logger.info(f"\n📋 Summary for {candidate['name']}:")
        for key, val in status.items():
            logger.info(f"   - {key.capitalize()}: {'✓' if val else '✗'}")

        return status

    def run(
        self,
        election_id: str,
        batch_size: int = 10,
        delay_between_candidates: float = 2.0,
        delay_between_requests: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Run the agent to populate data for multiple candidates.

        Args:
            election_id: Election ID to process
            batch_size: Number of candidates to process
            delay_between_candidates: Delay between processing candidates
            delay_between_requests: Delay between requests

        Returns:
            Summary statistics
        """
        logger.info("\n" + "=" * 60)
        logger.info("🚀 Starting Candidate Data Population Agent")
        logger.info("=" * 60 + "\n")
        logger.info(f"Election ID: {election_id}")
        logger.info(f"Batch size: {batch_size}")
        logger.info(f"Delay between candidates: {delay_between_candidates}s")
        logger.info(f"Delay between requests: {delay_between_requests}s\n")

        # Load all candidates
        all_candidates = self._load_candidates(election_id)
        if not all_candidates:
            logger.error(f"No candidates found for election: {election_id}")
            return {"total_processed": 0, "successful": 0, "partial": 0, "failed": 0}

        # Find candidates needing data
        candidates = self.find_candidates_needing_data(election_id, limit=batch_size)

        if not candidates:
            logger.info("✅ No candidates found needing data population")
            return {"total_processed": 0, "successful": 0, "partial": 0, "failed": 0}

        stats = {
            "total_processed": 0,
            "successful": 0,
            "partial": 0,
            "failed": 0,
        }

        # Create a lookup by ID for updates
        candidates_by_id = {c["id"]: c for c in all_candidates}

        for idx, candidate in enumerate(candidates, 1):
            logger.info(f"\nProcessing {idx}/{len(candidates)}")

            status = self.populate_candidate_data(
                candidate, election_id, delay_between_requests=delay_between_requests
            )

            # Update in the full list
            candidates_by_id[candidate["id"]] = candidate

            stats["total_processed"] += 1
            fields_populated = sum(status.values())
            if fields_populated == 6:
                stats["successful"] += 1
            elif fields_populated > 0:
                stats["partial"] += 1
            else:
                stats["failed"] += 1

            # Save after each candidate for incremental progress
            updated_candidates = list(candidates_by_id.values())
            self._save_candidates(election_id, updated_candidates)

            if idx < len(candidates):
                time.sleep(delay_between_candidates)

        logger.info("\n" + "=" * 60)
        logger.info("🎉 Agent Run Complete")
        logger.info("=" * 60 + "\n")
        logger.info(f"Total candidates processed: {stats['total_processed']}")
        logger.info(f"Fully populated (6/6 fields): {stats['successful']}")
        logger.info(f"Partially populated: {stats['partial']}")
        logger.info(f"Failed to populate: {stats['failed']}")
        logger.info("")

        return stats
