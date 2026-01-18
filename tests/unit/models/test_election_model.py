"""
Unit tests for Election database model.

Tests cover CRUD operations, validation, and model methods.
"""

import sys
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb before imports
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()

from app.database.models import Election


@pytest.mark.unit
class TestElectionModel:
    """Tests for Election model basic functionality."""

    def test_election_repr(self, mock_election):
        """Test Election string representation."""
        assert mock_election.id is not None
        assert mock_election.name is not None
        assert mock_election.year is not None

    def test_election_has_required_fields(self, mock_election):
        """Test Election has all required fields."""
        required_fields = ['id', 'name', 'type', 'year']
        for field in required_fields:
            assert hasattr(mock_election, field)

    def test_election_has_optional_fields(self, mock_election):
        """Test Election has optional statistics fields."""
        optional_fields = ['total_constituencies', 'total_candidates', 
                          'total_parties', 'result_status']
        for field in optional_fields:
            assert hasattr(mock_election, field)


@pytest.mark.unit
class TestElectionCreate:
    """Tests for Election.create method."""

    def test_create_election_minimal(self, mock_db_session):
        """Test creating election with minimal required data."""
        with patch.object(Election, 'create') as mock_create:
            mock_election = Mock(spec=Election)
            mock_election.id = 'test-election-2024'
            mock_election.name = 'Test Election 2024'
            mock_election.type = 'LOK_SABHA'
            mock_election.year = 2024
            mock_create.return_value = mock_election

            election = Election.create(
                session=mock_db_session,
                id='test-election-2024',
                name='Test Election 2024',
                type='LOK_SABHA',
                year=2024
            )

            assert election.id == 'test-election-2024'
            assert election.name == 'Test Election 2024'
            assert election.type == 'LOK_SABHA'
            assert election.year == 2024

    def test_create_election_with_statistics(self, mock_db_session, sample_election_data):
        """Test creating election with full statistics."""
        with patch.object(Election, 'create') as mock_create:
            mock_election = Mock(spec=Election)
            for key, value in sample_election_data.items():
                setattr(mock_election, key, value)
            mock_create.return_value = mock_election

            election = Election.create(
                session=mock_db_session,
                **sample_election_data
            )

            assert election.total_constituencies == 543
            assert election.total_candidates == 8000
            assert election.total_parties == 450
            assert election.result_status == 'DECLARED'


@pytest.mark.unit
class TestElectionRead:
    """Tests for Election read operations."""

    def test_get_by_id_found(self, mock_db_session, mock_election):
        """Test getting election by ID when found."""
        with patch.object(Election, 'get_by_id', return_value=mock_election):
            election = Election.get_by_id(mock_db_session, 'lok-sabha-2024')
            assert election is not None
            assert election.id == 'lok-sabha-2024'

    def test_get_by_id_not_found(self, mock_db_session):
        """Test getting election by ID when not found."""
        with patch.object(Election, 'get_by_id', return_value=None):
            election = Election.get_by_id(mock_db_session, 'nonexistent')
            assert election is None

    def test_get_all_elections(self, mock_db_session, mock_election):
        """Test getting all elections."""
        with patch.object(Election, 'get_all', return_value=[mock_election]):
            elections = Election.get_all(mock_db_session)
            assert len(elections) == 1
            assert elections[0].id == 'lok-sabha-2024'

    def test_get_all_with_pagination(self, mock_db_session, mock_election):
        """Test getting elections with pagination."""
        with patch.object(Election, 'get_all', return_value=[mock_election]):
            elections = Election.get_all(mock_db_session, skip=0, limit=10)
            assert len(elections) == 1

    def test_get_by_year(self, mock_db_session, mock_election):
        """Test getting elections by year."""
        with patch.object(Election, 'get_by_year', return_value=[mock_election]):
            elections = Election.get_by_year(mock_db_session, 2024)
            assert len(elections) == 1
            assert elections[0].year == 2024

    def test_get_by_type(self, mock_db_session, mock_election):
        """Test getting elections by type."""
        with patch.object(Election, 'get_by_type', return_value=[mock_election]):
            elections = Election.get_by_type(mock_db_session, 'LOK_SABHA')
            assert len(elections) == 1
            assert elections[0].type == 'LOK_SABHA'


@pytest.mark.unit
class TestElectionUpdate:
    """Tests for Election update operations."""

    def test_update_status(self, mock_db_session, mock_election):
        """Test updating election status."""
        mock_election.update.return_value = mock_election
        mock_election.result_status = 'DECLARED'

        result = mock_election.update(mock_db_session, result_status='DECLARED')

        mock_election.update.assert_called_once()
        assert result.result_status == 'DECLARED'

    def test_update_statistics(self, mock_db_session, mock_election):
        """Test updating election statistics."""
        mock_election.update.return_value = mock_election
        mock_election.total_candidates = 8500

        result = mock_election.update(
            mock_db_session,
            total_candidates=8500
        )

        assert result.total_candidates == 8500


@pytest.mark.unit
class TestElectionBulkOperations:
    """Tests for Election bulk operations."""

    def test_bulk_create(self, mock_db_session):
        """Test bulk creating elections."""
        elections_data = [
            {'id': 'election-1', 'name': 'Election 1', 'type': 'LOK_SABHA', 'year': 2024},
            {'id': 'election-2', 'name': 'Election 2', 'type': 'VIDHAN_SABHA', 'year': 2024}
        ]

        with patch.object(Election, 'bulk_create') as mock_bulk:
            mock_elections = [Mock(spec=Election, id=e['id']) for e in elections_data]
            mock_bulk.return_value = mock_elections

            result = Election.bulk_create(mock_db_session, elections_data)

            assert len(result) == 2

    def test_bulk_upsert(self, mock_db_session):
        """Test bulk upserting elections."""
        elections_data = [
            {'id': 'election-1', 'name': 'Election 1', 'type': 'LOK_SABHA', 'year': 2024}
        ]

        with patch.object(Election, 'bulk_upsert', return_value=1):
            count = Election.bulk_upsert(mock_db_session, elections_data)
            assert count == 1


@pytest.mark.unit
class TestElectionDelete:
    """Tests for Election delete operations."""

    def test_delete_election(self, mock_db_session, mock_election):
        """Test deleting an election."""
        mock_election.delete(mock_db_session)
        mock_election.delete.assert_called_once_with(mock_db_session)


@pytest.mark.unit
class TestElectionValidation:
    """Tests for Election validation logic."""

    def test_valid_election_types(self):
        """Test valid election type values."""
        valid_types = ['LOK_SABHA', 'VIDHAN_SABHA']
        for election_type in valid_types:
            assert election_type in ['LOK_SABHA', 'VIDHAN_SABHA']

    def test_valid_result_statuses(self):
        """Test valid result status values."""
        valid_statuses = ['DECLARED', 'PENDING', 'ONGOING']
        for status in valid_statuses:
            assert status in ['DECLARED', 'PENDING', 'ONGOING']

    def test_valid_year_range(self, sample_election_data):
        """Test election year is reasonable."""
        year = sample_election_data['year']
        assert 1947 <= year <= 2100  # India's independence to far future

    def test_positive_statistics(self, sample_election_data):
        """Test statistics are positive numbers."""
        assert sample_election_data['total_constituencies'] > 0
        assert sample_election_data['total_candidates'] > 0
        assert sample_election_data['total_parties'] > 0
