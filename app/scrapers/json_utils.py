"""
JSON utilities for election data handling.

Provides validation, safe read/write operations, and progress tracking
for election data stored in JSON files.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ElectionDataValidator:
    """Validates election data before saving."""

    @staticmethod
    def validate_candidate(candidate: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate candidate data.

        Args:
            candidate: Candidate dictionary

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        required_fields = ["id", "name", "party_id", "constituency_id", "state_id", "status"]

        for field in required_fields:
            if field not in candidate or candidate[field] is None:
                errors.append(f"Missing required field: {field}")

        if candidate.get("status") and candidate["status"] not in ["WON", "LOST", "INDEPENDENT"]:
            errors.append(f"Invalid status: {candidate.get('status')}")

        if candidate.get("type") and candidate["type"] not in ["MP", "MLA"]:
            errors.append(f"Invalid type: {candidate.get('type')}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_party(party: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate party data.

        Args:
            party: Party dictionary

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        required_fields = ["id", "name"]

        for field in required_fields:
            if field not in party or party[field] is None:
                errors.append(f"Missing required field: {field}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_constituency(constituency: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate constituency data.

        Args:
            constituency: Constituency dictionary

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        required_fields = ["id", "name", "state_id"]

        for field in required_fields:
            if field not in constituency or constituency[field] is None:
                errors.append(f"Missing required field: {field}")

        return len(errors) == 0, errors


class JsonFileManager:
    """Manages JSON file operations with safety features."""

    @staticmethod
    def load_json(file_path: Path) -> List[Dict[str, Any]]:
        """
        Safely load data from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            List of dictionaries, or empty list if file doesn't exist/is invalid
        """
        if not file_path.exists():
            logger.debug(f"File not found: {file_path}")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []

    @staticmethod
    def save_json(
        data: List[Dict[str, Any]],
        file_path: Path,
        create_backup: bool = True,
    ) -> bool:
        """
        Safely save data to JSON file with optional backup.

        Args:
            data: Data to save
            file_path: Target file path
            create_backup: Whether to create backup of existing file

        Returns:
            True if successful, False otherwise
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create backup if file exists
        if create_backup and file_path.exists():
            backup_path = file_path.with_suffix(f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            try:
                shutil.copy2(file_path, backup_path)
                logger.debug(f"Created backup: {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")

        try:
            # Write to temp file first, then rename
            temp_path = file_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            # Atomic rename
            temp_path.replace(file_path)
            logger.info(f"Saved {len(data)} records to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save {file_path}: {e}")
            return False

    @staticmethod
    def append_to_json(
        file_path: Path,
        data: Any,
        dedupe_key: Optional[str] = None,
    ) -> bool:
        """
        Append data to existing JSON file.

        Args:
            file_path: Target file path
            data: Data to append (dict or list)
            dedupe_key: Key to use for deduplication (e.g., 'id')

        Returns:
            True if successful, False otherwise
        """
        existing = JsonFileManager.load_json(file_path)

        if isinstance(data, list):
            new_items = data
        else:
            new_items = [data]

        if dedupe_key:
            existing_keys = {item.get(dedupe_key) for item in existing}
            new_items = [item for item in new_items if item.get(dedupe_key) not in existing_keys]

        existing.extend(new_items)
        return JsonFileManager.save_json(existing, file_path, create_backup=False)


class ScrapeProgressTracker:
    """Tracks scraping progress and provides resume capability."""

    def __init__(self, progress_file: Path):
        """
        Initialize progress tracker.

        Args:
            progress_file: Path to progress tracking file
        """
        self.progress_file = progress_file
        self.progress: Dict[str, Any] = self._load_progress()

    def _load_progress(self) -> Dict[str, Any]:
        """Load progress from file."""
        if not self.progress_file.exists():
            return {
                "started_at": datetime.now().isoformat(),
                "completed_parties": [],
                "completed_constituencies": [],
                "last_checkpoint": None,
                "stats": {
                    "total_parties": 0,
                    "total_constituencies": 0,
                    "total_candidates": 0,
                },
            }

        try:
            with open(self.progress_file, "r") as f:
                return json.load(f)
        except Exception:
            return self._load_progress()

    def _save_progress(self) -> None:
        """Save progress to file."""
        self.progress["last_checkpoint"] = datetime.now().isoformat()
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.progress_file, "w") as f:
            json.dump(self.progress, f, indent=2)

    def is_party_completed(self, party_id: str) -> bool:
        """Check if party scraping is completed."""
        return party_id in self.progress.get("completed_parties", [])

    def mark_party_completed(self, party_id: str) -> None:
        """Mark party as completed."""
        if party_id not in self.progress["completed_parties"]:
            self.progress["completed_parties"].append(party_id)
            self._save_progress()

    def is_constituency_completed(self, constituency_id: str) -> bool:
        """Check if constituency scraping is completed."""
        return constituency_id in self.progress.get("completed_constituencies", [])

    def mark_constituency_completed(self, constituency_id: str) -> None:
        """Mark constituency as completed."""
        if constituency_id not in self.progress["completed_constituencies"]:
            self.progress["completed_constituencies"].append(constituency_id)
            self._save_progress()

    def update_stats(self, **kwargs) -> None:
        """Update statistics."""
        for key, value in kwargs.items():
            self.progress["stats"][key] = value
        self._save_progress()

    def get_summary(self) -> str:
        """Get progress summary string."""
        stats = self.progress.get("stats", {})
        return (
            f"Progress: "
            f"{len(self.progress.get('completed_parties', []))} parties, "
            f"{len(self.progress.get('completed_constituencies', []))} constituencies, "
            f"{stats.get('total_candidates', 0)} candidates"
        )

    def reset(self) -> None:
        """Reset progress (start fresh)."""
        self.progress = self._load_progress()
        self.progress["started_at"] = datetime.now().isoformat()
        self.progress["completed_parties"] = []
        self.progress["completed_constituencies"] = []
        self._save_progress()
