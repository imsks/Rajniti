"""
Unit tests for Candidate database model.

Tests cover CRUD operations, validation, and model methods.
"""

import sys
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb before imports
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()

from app.database.models import Candidate


@pytest.mark.unit
class TestCandidateModel:
    """Tests for Candidate model basic functionality."""

    def test_candidate_repr(self, mock_candidate):
        """Test Candidate string representation."""
        assert mock_candidate.id is not None
        assert mock_candidate.name is not None
        assert mock_candidate.party_id is not None

    def test_candidate_has_required_fields(self, mock_candidate):
        """Test Candidate has all required fields."""
        required_fields = [
            'id', 'name', 'party_id', 'constituency_id', 'state_id',
            'status', 'type', 'image_url'
        ]
        for field in required_fields:
            assert hasattr(mock_candidate, field)

    def test_candidate_has_detailed_fields(self, mock_candidate):
        """Test Candidate has detailed information fields."""
        detailed_fields = [
            'education_background', 'political_background', 'family_background',
            'assets', 'liabilities', 'crime_cases'
        ]
        for field in detailed_fields:
            assert hasattr(mock_candidate, field)


@pytest.mark.unit
class TestCandidateCreate:
    """Tests for Candidate.create method."""

    def test_create_candidate_minimal(self, mock_db_session):
        """Test creating candidate with minimal required data."""
        with patch.object(Candidate, 'create') as mock_create:
            mock_candidate = Mock(spec=Candidate)
            mock_candidate.id = 'new-candidate'
            mock_candidate.name = 'New Candidate'
            mock_candidate.party_id = 'BJP'
            mock_candidate.constituency_id = 'DL-1'
            mock_candidate.state_id = 'DL'
            mock_candidate.status = 'LOST'
            mock_candidate.type = 'MP'
            mock_create.return_value = mock_candidate

            candidate = Candidate.create(
                session=mock_db_session,
                id='new-candidate',
                name='New Candidate',
                party_id='BJP',
                constituency_id='DL-1',
                state_id='DL',
                status='LOST'
            )

            assert candidate.id == 'new-candidate'
            assert candidate.name == 'New Candidate'
            assert candidate.status == 'LOST'

    def test_create_candidate_with_detailed_info(self, mock_db_session, sample_candidate_data):
        """Test creating candidate with detailed information."""
        with patch.object(Candidate, 'create') as mock_create:
            mock_candidate = Mock(spec=Candidate)
            for key, value in sample_candidate_data.items():
                setattr(mock_candidate, key, value)
            mock_create.return_value = mock_candidate

            candidate = Candidate.create(
                session=mock_db_session,
                id=sample_candidate_data['id'],
                name=sample_candidate_data['name'],
                party_id=sample_candidate_data['party_id'],
                constituency_id=sample_candidate_data['constituency_id'],
                state_id=sample_candidate_data['state_id'],
                status=sample_candidate_data['status'],
                education_background=sample_candidate_data['education_background'],
                political_background=sample_candidate_data['political_background']
            )

            assert candidate.education_background is not None
            assert candidate.political_background is not None


@pytest.mark.unit
class TestCandidateRead:
    """Tests for Candidate read operations."""

    def test_get_by_id_found(self, mock_db_session, mock_candidate):
        """Test getting candidate by ID when found."""
        with patch.object(Candidate, 'get_by_id', return_value=mock_candidate):
            candidate = Candidate.get_by_id(mock_db_session, 'test-candidate-123')
            assert candidate is not None
            assert candidate.id == 'test-candidate-123'

    def test_get_by_id_not_found(self, mock_db_session):
        """Test getting candidate by ID when not found."""
        with patch.object(Candidate, 'get_by_id', return_value=None):
            candidate = Candidate.get_by_id(mock_db_session, 'nonexistent')
            assert candidate is None

    def test_get_by_party(self, mock_db_session, mock_candidate):
        """Test getting candidates by party."""
        with patch.object(Candidate, 'get_by_party', return_value=[mock_candidate]):
            candidates = Candidate.get_by_party(mock_db_session, 'BJP')
            assert len(candidates) == 1
            assert candidates[0].party_id == 'BJP'

    def test_get_by_constituency(self, mock_db_session, mock_candidate):
        """Test getting candidates by constituency."""
        with patch.object(Candidate, 'get_by_constituency', return_value=[mock_candidate]):
            candidates = Candidate.get_by_constituency(mock_db_session, 'DL-1')
            assert len(candidates) == 1
            assert candidates[0].constituency_id == 'DL-1'

    def test_get_winners(self, mock_db_session, mock_candidate):
        """Test getting winning candidates."""
        mock_candidate.status = 'WON'
        with patch.object(Candidate, 'get_winners', return_value=[mock_candidate]):
            winners = Candidate.get_winners(mock_db_session)
            assert len(winners) == 1
            assert winners[0].status == 'WON'

    def test_search_by_name(self, mock_db_session, mock_candidate):
        """Test searching candidates by name."""
        with patch.object(Candidate, 'search_by_name', return_value=[mock_candidate]):
            candidates = Candidate.search_by_name(mock_db_session, 'Test')
            assert len(candidates) == 1
            assert 'Test' in candidates[0].name

    def test_get_all_with_pagination(self, mock_db_session, mock_candidate):
        """Test getting all candidates with pagination."""
        with patch.object(Candidate, 'get_all', return_value=[mock_candidate]):
            candidates = Candidate.get_all(mock_db_session, skip=0, limit=10)
            assert len(candidates) == 1


@pytest.mark.unit
class TestCandidateUpdate:
    """Tests for Candidate update operations."""

    def test_update_status(self, mock_db_session, mock_candidate):
        """Test updating candidate status."""
        mock_candidate.update.return_value = mock_candidate
        mock_candidate.status = 'WON'

        result = mock_candidate.update(mock_db_session, status='WON')

        mock_candidate.update.assert_called_once()
        assert result.status == 'WON'

    def test_update_detailed_info(self, mock_db_session, mock_candidate):
        """Test updating detailed information."""
        new_education = [{'year': '2005', 'college': 'IIT Delhi', 'stream': 'Engineering'}]
        mock_candidate.update.return_value = mock_candidate
        mock_candidate.education_background = new_education

        result = mock_candidate.update(
            mock_db_session,
            education_background=new_education
        )

        assert result.education_background == new_education


@pytest.mark.unit
class TestCandidateBulkOperations:
    """Tests for Candidate bulk operations."""

    def test_bulk_create(self, mock_db_session, generate_candidates):
        """Test bulk creating candidates."""
        candidates_data = generate_candidates(3)

        with patch.object(Candidate, 'bulk_create') as mock_bulk:
            mock_candidates = [Mock(spec=Candidate, id=c['id']) for c in candidates_data]
            mock_bulk.return_value = mock_candidates

            result = Candidate.bulk_create(mock_db_session, candidates_data)

            assert len(result) == 3
            mock_bulk.assert_called_once()

    def test_bulk_upsert(self, mock_db_session, generate_candidates):
        """Test bulk upserting candidates."""
        candidates_data = generate_candidates(3)

        with patch.object(Candidate, 'bulk_upsert', return_value=3):
            count = Candidate.bulk_upsert(mock_db_session, candidates_data)

            assert count == 3

    def test_bulk_upsert_empty_list(self, mock_db_session):
        """Test bulk upsert with empty list."""
        with patch.object(Candidate, 'bulk_upsert', return_value=0):
            count = Candidate.bulk_upsert(mock_db_session, [])
            assert count == 0


@pytest.mark.unit
class TestCandidateDelete:
    """Tests for Candidate delete operations."""

    def test_delete_candidate(self, mock_db_session, mock_candidate):
        """Test deleting a candidate."""
        mock_candidate.delete(mock_db_session)
        mock_candidate.delete.assert_called_once_with(mock_db_session)


@pytest.mark.unit
class TestCandidateValidation:
    """Tests for Candidate validation logic."""

    def test_valid_status_values(self):
        """Test valid status values."""
        valid_statuses = ['WON', 'LOST']
        for status in valid_statuses:
            assert status in ['WON', 'LOST']

    def test_valid_type_values(self):
        """Test valid candidate type values."""
        valid_types = ['MP', 'MLA']
        for candidate_type in valid_types:
            assert candidate_type in ['MP', 'MLA']

    def test_education_background_structure(self, sample_candidate_data):
        """Test education background has correct structure."""
        education = sample_candidate_data['education_background'][0]
        assert 'year' in education
        assert 'college' in education
        assert 'stream' in education

    def test_political_background_structure(self, sample_candidate_data):
        """Test political background has correct structure."""
        political = sample_candidate_data['political_background'][0]
        assert 'election_year' in political
        assert 'party' in political
        assert 'result' in political

    def test_assets_structure(self, sample_candidate_data):
        """Test assets has correct structure."""
        asset = sample_candidate_data['assets'][0]
        assert 'type' in asset
        assert 'amount' in asset
        assert isinstance(asset['amount'], (int, float))

    def test_crime_cases_structure(self, sample_candidate_data):
        """Test crime cases has correct structure."""
        crime = sample_candidate_data['crime_cases'][0]
        assert 'fir_no' in crime
        assert 'charges_framed' in crime
        assert isinstance(crime['charges_framed'], bool)
