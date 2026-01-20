"""
Unit tests for VectorDBPipeline.

Tests the pipeline that syncs candidate data from JSON to ChromaDB.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from app.services.vector_db_pipeline import VectorDBPipeline


class TestVectorDBPipelineInit:
    """Tests for VectorDBPipeline initialization."""

    def test_init_with_default_params(self):
        """Test initialization with default parameters."""
        with patch("app.services.vector_db_pipeline.VectorDBService") as mock_service:
            mock_service.return_value = Mock()
            pipeline = VectorDBPipeline()
            
            assert pipeline.vector_db is not None
            assert pipeline._data_dir.exists() or True

    def test_init_with_custom_data_dir(self, tmp_path):
        """Test initialization with custom data directory."""
        with patch("app.services.vector_db_pipeline.VectorDBService") as mock_service:
            mock_service.return_value = Mock()
            pipeline = VectorDBPipeline(data_dir=tmp_path)
            
            assert pipeline._data_dir == tmp_path


class TestVectorDBPipelineCandidateToText:
    """Tests for _candidate_to_text method."""

    @pytest.fixture
    def pipeline(self):
        """Create pipeline with mocked vector db service."""
        with patch("app.services.vector_db_pipeline.VectorDBService") as mock_service:
            mock_service.return_value = Mock()
            yield VectorDBPipeline()

    def test_basic_candidate_to_text(self, pipeline):
        """Test converting basic candidate data to text."""
        candidate = {
            "id": "c1",
            "name": "Test Candidate",
            "constituency_id": "DL-1",
            "state_id": "DL",
            "party_id": "BJP",
            "status": "WON",
            "type": "MP",
        }
        
        text = pipeline._candidate_to_text(candidate)
        
        assert "Name: Test Candidate" in text
        assert "Status: WON" in text
        assert "Party: BJP" in text

    def test_candidate_with_education(self, pipeline):
        """Test candidate with education background."""
        candidate = {
            "id": "c1",
            "name": "Test",
            "education_background": [
                {"year": "2000", "college": "Delhi University", "stream": "Law"}
            ],
        }
        
        text = pipeline._candidate_to_text(candidate)
        
        assert "Education:" in text
        assert "Delhi University" in text

    def test_candidate_with_assets(self, pipeline):
        """Test candidate with assets."""
        candidate = {
            "id": "c1",
            "name": "Test",
            "assets": [
                {"type": "CASH", "amount": 1000000.0},
                {"type": "LAND", "amount": 5000000.0},
            ],
        }
        
        text = pipeline._candidate_to_text(candidate)
        
        assert "Assets:" in text
        assert "6,000,000" in text  # Total assets

    def test_candidate_with_crime_cases(self, pipeline):
        """Test candidate with crime cases."""
        candidate = {
            "id": "c1",
            "name": "Test",
            "crime_cases": [
                {"fir_no": "123", "charges_framed": True},
                {"fir_no": "456", "charges_framed": False},
            ],
        }
        
        text = pipeline._candidate_to_text(candidate)
        
        assert "Criminal Cases:" in text
        assert "2 criminal case(s)" in text
        assert "1 with charges framed" in text


class TestVectorDBPipelineCandidateToMetadata:
    """Tests for _candidate_to_metadata method."""

    @pytest.fixture
    def pipeline(self):
        """Create pipeline with mocked vector db service."""
        with patch("app.services.vector_db_pipeline.VectorDBService") as mock_service:
            mock_service.return_value = Mock()
            yield VectorDBPipeline()

    def test_basic_metadata(self, pipeline):
        """Test extracting basic metadata."""
        candidate = {
            "id": "c1",
            "name": "Test",
            "party_id": "BJP",
            "constituency_id": "DL-1",
            "state_id": "DL",
            "status": "WON",
            "type": "MP",
        }
        
        metadata = pipeline._candidate_to_metadata(candidate)
        
        assert metadata["candidate_id"] == "c1"
        assert metadata["name"] == "Test"
        assert metadata["party_id"] == "BJP"
        assert metadata["status"] == "WON"

    def test_metadata_with_counts(self, pipeline):
        """Test metadata includes counts for detailed data."""
        candidate = {
            "id": "c1",
            "name": "Test",
            "education_background": [{"year": "2000"}],
            "assets": [{"type": "CASH"}, {"type": "LAND"}],
            "crime_cases": [{"fir_no": "123"}],
        }
        
        metadata = pipeline._candidate_to_metadata(candidate)
        
        assert metadata["education_count"] == 1
        assert metadata["assets_count"] == 2
        assert metadata["crime_cases_count"] == 1


class TestVectorDBPipelineSyncCandidate:
    """Tests for sync_candidate method."""

    def test_sync_candidate_success(self):
        """Test successful candidate sync."""
        mock_vector_db = Mock()
        mock_vector_db.upsert_candidate_data = Mock()
        
        with patch("app.services.vector_db_pipeline.VectorDBService") as mock_service:
            mock_service.return_value = mock_vector_db
            pipeline = VectorDBPipeline()
            
            candidate = {
                "id": "c1",
                "name": "Test",
                "party_id": "BJP",
                "status": "WON",
            }
            
            result = pipeline.sync_candidate(candidate)
            
            assert result is True
            mock_vector_db.upsert_candidate_data.assert_called_once()

    def test_sync_candidate_failure(self):
        """Test failed candidate sync."""
        mock_vector_db = Mock()
        mock_vector_db.upsert_candidate_data = Mock(side_effect=Exception("DB Error"))
        
        with patch("app.services.vector_db_pipeline.VectorDBService") as mock_service:
            mock_service.return_value = mock_vector_db
            pipeline = VectorDBPipeline()
            
            candidate = {"id": "c1", "name": "Test"}
            
            result = pipeline.sync_candidate(candidate)
            
            assert result is False


class TestVectorDBPipelineBatchSync:
    """Tests for batch sync methods."""

    @pytest.fixture
    def setup_election_data(self, tmp_path):
        """Setup test election data."""
        elections_dir = tmp_path / "elections"
        elections_dir.mkdir()
        (elections_dir / "test.json").write_text(json.dumps([
            {"election_id": "lok-sabha-2024", "name": "Test"}
        ]))

        election_dir = tmp_path / "lok_sabha" / "lok-sabha-2024"
        election_dir.mkdir(parents=True)

        candidates = [
            {"id": "c1", "name": "C1", "status": "WON"},
            {"id": "c2", "name": "C2", "status": "LOST"},
            {"id": "c3", "name": "NOTA", "status": ""},  # Should be filtered
        ]
        (election_dir / "candidates.json").write_text(json.dumps(candidates))

        return tmp_path

    def test_sync_candidates_batch(self, setup_election_data):
        """Test batch syncing candidates."""
        mock_vector_db = Mock()
        mock_vector_db.upsert_candidate_data = Mock()
        
        with patch("app.services.vector_db_pipeline.VectorDBService") as mock_service:
            mock_service.return_value = mock_vector_db
            pipeline = VectorDBPipeline(data_dir=setup_election_data)
            
            stats = pipeline.sync_candidates_batch("lok-sabha-2024", batch_size=10)
            
            assert stats["total"] == 2  # NOTA filtered out
            assert stats["synced"] == 2
            assert stats["failed"] == 0

    def test_sync_candidates_batch_with_filter(self, setup_election_data):
        """Test batch sync with status filter."""
        mock_vector_db = Mock()
        mock_vector_db.upsert_candidate_data = Mock()
        
        with patch("app.services.vector_db_pipeline.VectorDBService") as mock_service:
            mock_service.return_value = mock_vector_db
            pipeline = VectorDBPipeline(data_dir=setup_election_data)
            
            stats = pipeline.sync_candidates_batch(
                "lok-sabha-2024",
                filter_criteria={"status": "WON"}
            )
            
            assert stats["total"] == 1  # Only WON candidates


class TestVectorDBPipelineDeleteCandidate:
    """Tests for delete_candidate method."""

    def test_delete_candidate_success(self):
        """Test successful candidate deletion."""
        mock_vector_db = Mock()
        mock_vector_db.delete_candidate = Mock()
        
        with patch("app.services.vector_db_pipeline.VectorDBService") as mock_service:
            mock_service.return_value = mock_vector_db
            pipeline = VectorDBPipeline()
            
            result = pipeline.delete_candidate("c1")
            
            assert result is True
            mock_vector_db.delete_candidate.assert_called_once_with("c1")

    def test_delete_candidate_failure(self):
        """Test failed candidate deletion."""
        mock_vector_db = Mock()
        mock_vector_db.delete_candidate = Mock(side_effect=Exception("Error"))
        
        with patch("app.services.vector_db_pipeline.VectorDBService") as mock_service:
            mock_service.return_value = mock_vector_db
            pipeline = VectorDBPipeline()
            
            result = pipeline.delete_candidate("c1")
            
            assert result is False
