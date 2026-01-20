"""
Unit tests for JSON utilities.

Tests validation, file operations, and progress tracking.
"""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from app.scrapers.json_utils import (
    ElectionDataValidator,
    JsonFileManager,
    ScrapeProgressTracker,
)


class TestElectionDataValidator:
    """Tests for ElectionDataValidator."""

    def test_validate_candidate_valid(self):
        """Test validating a valid candidate."""
        candidate = {
            "id": "c1",
            "name": "Test Candidate",
            "party_id": "BJP",
            "constituency_id": "DL-1",
            "state_id": "DL",
            "status": "WON",
            "type": "MP",
        }

        is_valid, errors = ElectionDataValidator.validate_candidate(candidate)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_candidate_missing_fields(self):
        """Test validating candidate with missing fields."""
        candidate = {"id": "c1", "name": "Test"}

        is_valid, errors = ElectionDataValidator.validate_candidate(candidate)

        assert is_valid is False
        assert len(errors) > 0
        assert any("party_id" in e for e in errors)

    def test_validate_candidate_invalid_status(self):
        """Test validating candidate with invalid status."""
        candidate = {
            "id": "c1",
            "name": "Test",
            "party_id": "BJP",
            "constituency_id": "DL-1",
            "state_id": "DL",
            "status": "INVALID",
        }

        is_valid, errors = ElectionDataValidator.validate_candidate(candidate)

        assert is_valid is False
        assert any("status" in e for e in errors)

    def test_validate_party_valid(self):
        """Test validating a valid party."""
        party = {"id": "BJP", "name": "Bharatiya Janata Party"}

        is_valid, errors = ElectionDataValidator.validate_party(party)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_party_missing_name(self):
        """Test validating party without name."""
        party = {"id": "BJP"}

        is_valid, errors = ElectionDataValidator.validate_party(party)

        assert is_valid is False
        assert any("name" in e for e in errors)

    def test_validate_constituency_valid(self):
        """Test validating a valid constituency."""
        constituency = {"id": "DL-1", "name": "New Delhi", "state_id": "DL"}

        is_valid, errors = ElectionDataValidator.validate_constituency(constituency)

        assert is_valid is True
        assert len(errors) == 0


class TestJsonFileManager:
    """Tests for JsonFileManager."""

    def test_load_json_existing_file(self, tmp_path):
        """Test loading existing JSON file."""
        file_path = tmp_path / "test.json"
        data = [{"id": "1"}, {"id": "2"}]
        file_path.write_text(json.dumps(data))

        result = JsonFileManager.load_json(file_path)

        assert result == data

    def test_load_json_nonexistent_file(self, tmp_path):
        """Test loading non-existent file returns empty list."""
        file_path = tmp_path / "nonexistent.json"

        result = JsonFileManager.load_json(file_path)

        assert result == []

    def test_load_json_invalid_json(self, tmp_path):
        """Test loading invalid JSON returns empty list."""
        file_path = tmp_path / "invalid.json"
        file_path.write_text("not valid json{")

        result = JsonFileManager.load_json(file_path)

        assert result == []

    def test_save_json_creates_file(self, tmp_path):
        """Test saving JSON creates file."""
        file_path = tmp_path / "new.json"
        data = [{"id": "1"}]

        result = JsonFileManager.save_json(data, file_path)

        assert result is True
        assert file_path.exists()
        loaded = json.loads(file_path.read_text())
        assert loaded == data

    def test_save_json_creates_directories(self, tmp_path):
        """Test saving JSON creates parent directories."""
        file_path = tmp_path / "nested" / "dir" / "test.json"
        data = [{"id": "1"}]

        result = JsonFileManager.save_json(data, file_path)

        assert result is True
        assert file_path.exists()

    def test_save_json_creates_backup(self, tmp_path):
        """Test saving JSON creates backup of existing file."""
        file_path = tmp_path / "test.json"
        original_data = [{"id": "original"}]
        file_path.write_text(json.dumps(original_data))

        new_data = [{"id": "new"}]
        JsonFileManager.save_json(new_data, file_path, create_backup=True)

        # Check backup was created
        backups = list(tmp_path.glob("*.backup.*.json"))
        assert len(backups) == 1

    def test_append_to_json(self, tmp_path):
        """Test appending data to JSON file."""
        file_path = tmp_path / "test.json"
        initial_data = [{"id": "1"}]
        file_path.write_text(json.dumps(initial_data))

        JsonFileManager.append_to_json(file_path, {"id": "2"})

        loaded = json.loads(file_path.read_text())
        assert len(loaded) == 2

    def test_append_to_json_with_dedup(self, tmp_path):
        """Test appending with deduplication."""
        file_path = tmp_path / "test.json"
        initial_data = [{"id": "1", "name": "Original"}]
        file_path.write_text(json.dumps(initial_data))

        # Try to append duplicate
        JsonFileManager.append_to_json(file_path, {"id": "1", "name": "Duplicate"}, dedupe_key="id")

        loaded = json.loads(file_path.read_text())
        assert len(loaded) == 1  # No duplicate added
        assert loaded[0]["name"] == "Original"


class TestScrapeProgressTracker:
    """Tests for ScrapeProgressTracker."""

    def test_init_creates_progress(self, tmp_path):
        """Test initialization creates progress structure."""
        progress_file = tmp_path / "progress.json"

        tracker = ScrapeProgressTracker(progress_file)

        assert "started_at" in tracker.progress
        assert "completed_parties" in tracker.progress
        assert "completed_constituencies" in tracker.progress

    def test_mark_party_completed(self, tmp_path):
        """Test marking party as completed."""
        progress_file = tmp_path / "progress.json"
        tracker = ScrapeProgressTracker(progress_file)

        tracker.mark_party_completed("BJP")

        assert tracker.is_party_completed("BJP") is True
        assert tracker.is_party_completed("INC") is False

    def test_mark_constituency_completed(self, tmp_path):
        """Test marking constituency as completed."""
        progress_file = tmp_path / "progress.json"
        tracker = ScrapeProgressTracker(progress_file)

        tracker.mark_constituency_completed("DL-1")

        assert tracker.is_constituency_completed("DL-1") is True

    def test_update_stats(self, tmp_path):
        """Test updating statistics."""
        progress_file = tmp_path / "progress.json"
        tracker = ScrapeProgressTracker(progress_file)

        tracker.update_stats(total_candidates=100, total_parties=10)

        assert tracker.progress["stats"]["total_candidates"] == 100
        assert tracker.progress["stats"]["total_parties"] == 10

    def test_get_summary(self, tmp_path):
        """Test getting progress summary."""
        progress_file = tmp_path / "progress.json"
        tracker = ScrapeProgressTracker(progress_file)
        tracker.mark_party_completed("BJP")
        tracker.update_stats(total_candidates=50)

        summary = tracker.get_summary()

        assert "1 parties" in summary
        assert "50 candidates" in summary

    def test_reset(self, tmp_path):
        """Test resetting progress."""
        progress_file = tmp_path / "progress.json"
        tracker = ScrapeProgressTracker(progress_file)
        tracker.mark_party_completed("BJP")

        tracker.reset()

        assert tracker.is_party_completed("BJP") is False

    def test_persists_progress(self, tmp_path):
        """Test that progress is persisted to file."""
        progress_file = tmp_path / "progress.json"

        # First tracker
        tracker1 = ScrapeProgressTracker(progress_file)
        tracker1.mark_party_completed("BJP")

        # Second tracker (should load persisted data)
        tracker2 = ScrapeProgressTracker(progress_file)

        assert tracker2.is_party_completed("BJP") is True
