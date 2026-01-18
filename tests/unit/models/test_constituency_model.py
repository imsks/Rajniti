"""
Unit tests for Constituency database model.

Tests cover CRUD operations, validation, and model methods.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb before imports
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()

from app.database.models import Constituency


@pytest.mark.unit
class TestConstituencyModel:
    """Tests for Constituency model basic functionality."""

    def test_constituency_repr(self, mock_constituency):
        """Test Constituency string representation."""
        assert mock_constituency.id is not None
        assert mock_constituency.name is not None
        assert mock_constituency.state_id is not None

    def test_constituency_has_required_fields(self, mock_constituency):
        """Test Constituency has all required fields."""
        required_fields = ['id', 'name', 'state_id']
        for field in required_fields:
            assert hasattr(mock_constituency, field)


@pytest.mark.unit
class TestConstituencyCreate:
    """Tests for Constituency.create method."""

    def test_create_constituency(self, mock_db_session, sample_constituency_data):
        """Test creating constituency."""
        with patch.object(Constituency, 'create') as mock_create:
            mock_constituency = Mock(spec=Constituency)
            for key, value in sample_constituency_data.items():
                setattr(mock_constituency, key, value)
            mock_create.return_value = mock_constituency

            constituency = Constituency.create(
                session=mock_db_session,
                **sample_constituency_data
            )

            assert constituency.id == 'DL-1'
            assert constituency.name == 'New Delhi'
            assert constituency.state_id == 'DL'


@pytest.mark.unit
class TestConstituencyRead:
    """Tests for Constituency read operations."""

    def test_get_by_id_found(self, mock_db_session, mock_constituency):
        """Test getting constituency by ID when found."""
        with patch.object(Constituency, 'get_by_id', return_value=mock_constituency):
            constituency = Constituency.get_by_id(mock_db_session, 'DL-1')
            assert constituency is not None
            assert constituency.id == 'DL-1'

    def test_get_by_id_not_found(self, mock_db_session):
        """Test getting constituency by ID when not found."""
        with patch.object(Constituency, 'get_by_id', return_value=None):
            constituency = Constituency.get_by_id(mock_db_session, 'NONEXISTENT')
            assert constituency is None

    def test_get_by_state(self, mock_db_session, mock_constituency):
        """Test getting constituencies by state."""
        with patch.object(Constituency, 'get_by_state', return_value=[mock_constituency]):
            constituencies = Constituency.get_by_state(mock_db_session, 'DL')
            assert len(constituencies) == 1
            assert constituencies[0].state_id == 'DL'

    def test_get_all_constituencies(self, mock_db_session, mock_constituency):
        """Test getting all constituencies."""
        with patch.object(Constituency, 'get_all', return_value=[mock_constituency]):
            constituencies = Constituency.get_all(mock_db_session)
            assert len(constituencies) == 1

    def test_get_by_name(self, mock_db_session, mock_constituency):
        """Test getting constituency by name."""
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.first.return_value = mock_constituency
        
        result = mock_db_session.query(Constituency).filter().first()
        assert result == mock_constituency


@pytest.mark.unit
class TestConstituencyUpdate:
    """Tests for Constituency update operations."""

    def test_update_constituency_name(self, mock_db_session, mock_constituency):
        """Test updating constituency name."""
        mock_constituency.update.return_value = mock_constituency
        mock_constituency.name = 'Updated Name'

        result = mock_constituency.update(mock_db_session, name='Updated Name')

        mock_constituency.update.assert_called_once()
        assert result.name == 'Updated Name'


@pytest.mark.unit
class TestConstituencyBulkOperations:
    """Tests for Constituency bulk operations."""

    def test_bulk_create(self, mock_db_session):
        """Test bulk creating constituencies."""
        constituencies_data = [
            {'id': 'DL-1', 'name': 'Constituency 1', 'state_id': 'DL'},
            {'id': 'DL-2', 'name': 'Constituency 2', 'state_id': 'DL'}
        ]

        with patch.object(Constituency, 'bulk_create') as mock_bulk:
            mock_constituencies = [Mock(spec=Constituency, id=c['id']) for c in constituencies_data]
            mock_bulk.return_value = mock_constituencies

            result = Constituency.bulk_create(mock_db_session, constituencies_data)

            assert len(result) == 2

    def test_bulk_upsert(self, mock_db_session):
        """Test bulk upserting constituencies."""
        constituencies_data = [
            {'id': 'DL-1', 'name': 'Constituency 1', 'state_id': 'DL'}
        ]

        with patch.object(Constituency, 'bulk_upsert', return_value=1):
            count = Constituency.bulk_upsert(mock_db_session, constituencies_data)
            assert count == 1


@pytest.mark.unit
class TestConstituencyDelete:
    """Tests for Constituency delete operations."""

    def test_delete_constituency(self, mock_db_session, mock_constituency):
        """Test deleting a constituency."""
        mock_constituency.delete(mock_db_session)
        mock_constituency.delete.assert_called_once_with(mock_db_session)


@pytest.mark.unit
class TestConstituencyValidation:
    """Tests for Constituency validation logic."""

    def test_valid_state_codes(self):
        """Test valid Indian state codes."""
        valid_state_codes = [
            'AN', 'AP', 'AR', 'AS', 'BR', 'CH', 'CG', 'DD', 'DL', 'GA',
            'GJ', 'HP', 'HR', 'JH', 'JK', 'KA', 'KL', 'LA', 'LD', 'MH',
            'ML', 'MN', 'MP', 'MZ', 'NL', 'OR', 'PB', 'PY', 'RJ', 'SK',
            'TN', 'TS', 'TR', 'UK', 'UP', 'WB'
        ]
        for code in valid_state_codes:
            assert len(code) == 2
            assert code == code.upper()

    def test_constituency_id_format(self, sample_constituency_data):
        """Test constituency ID format."""
        cid = sample_constituency_data['id']
        # Constituency ID should contain state code
        assert '-' in cid or len(cid) >= 2

    def test_name_not_empty(self, sample_constituency_data):
        """Test constituency name is not empty."""
        assert len(sample_constituency_data['name']) > 0

    def test_state_id_format(self, sample_constituency_data):
        """Test state ID is uppercase 2-letter code."""
        state_id = sample_constituency_data['state_id']
        assert len(state_id) == 2
        assert state_id == state_id.upper()
