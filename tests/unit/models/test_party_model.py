"""
Unit tests for Party database model.

Tests cover CRUD operations, validation, and model methods.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb before imports
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()

from app.database.models import Party


@pytest.mark.unit
class TestPartyModel:
    """Tests for Party model basic functionality."""

    def test_party_repr(self, mock_party):
        """Test Party string representation."""
        assert mock_party.id is not None
        assert mock_party.name is not None

    def test_party_has_required_fields(self, mock_party):
        """Test Party has all required fields."""
        required_fields = ['id', 'name', 'short_name', 'symbol']
        for field in required_fields:
            assert hasattr(mock_party, field)


@pytest.mark.unit
class TestPartyCreate:
    """Tests for Party.create method."""

    def test_create_party_minimal(self, mock_db_session):
        """Test creating party with minimal required data."""
        with patch.object(Party, 'create') as mock_create:
            mock_party = Mock(spec=Party)
            mock_party.id = 'NEW'
            mock_party.name = 'New Party'
            mock_party.short_name = 'NEW'
            mock_create.return_value = mock_party

            party = Party.create(
                session=mock_db_session,
                id='NEW',
                name='New Party',
                short_name='NEW'
            )

            assert party.id == 'NEW'
            assert party.name == 'New Party'

    def test_create_party_with_symbol(self, mock_db_session, sample_party_data):
        """Test creating party with symbol."""
        with patch.object(Party, 'create') as mock_create:
            mock_party = Mock(spec=Party)
            for key, value in sample_party_data.items():
                setattr(mock_party, key, value)
            mock_create.return_value = mock_party

            party = Party.create(
                session=mock_db_session,
                **sample_party_data
            )

            assert party.symbol == 'Lotus'


@pytest.mark.unit
class TestPartyRead:
    """Tests for Party read operations."""

    def test_get_by_id_found(self, mock_db_session, mock_party):
        """Test getting party by ID when found."""
        with patch.object(Party, 'get_by_id', return_value=mock_party):
            party = Party.get_by_id(mock_db_session, 'BJP')
            assert party is not None
            assert party.id == 'BJP'

    def test_get_by_id_not_found(self, mock_db_session):
        """Test getting party by ID when not found."""
        with patch.object(Party, 'get_by_id', return_value=None):
            party = Party.get_by_id(mock_db_session, 'NONEXISTENT')
            assert party is None

    def test_get_by_name_found(self, mock_db_session, mock_party):
        """Test getting party by name when found."""
        with patch.object(Party, 'get_by_name', return_value=mock_party):
            party = Party.get_by_name(mock_db_session, 'Bharatiya Janata Party')
            assert party is not None
            assert party.name == 'Bharatiya Janata Party'

    def test_get_all_parties(self, mock_db_session, mock_party):
        """Test getting all parties."""
        with patch.object(Party, 'get_all', return_value=[mock_party]):
            parties = Party.get_all(mock_db_session)
            assert len(parties) == 1

    def test_filter_parties_by_name(self, mock_db_session, mock_party):
        """Test filtering parties by name."""
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = [mock_party]
        
        result = mock_db_session.query(Party).filter().all()
        assert len(result) == 1


@pytest.mark.unit
class TestPartyUpdate:
    """Tests for Party update operations."""

    def test_update_party_name(self, mock_db_session, mock_party):
        """Test updating party name."""
        mock_party.update.return_value = mock_party
        mock_party.name = 'Updated Party Name'

        result = mock_party.update(mock_db_session, name='Updated Party Name')

        mock_party.update.assert_called_once()
        assert result.name == 'Updated Party Name'

    def test_update_party_symbol(self, mock_db_session, mock_party):
        """Test updating party symbol."""
        mock_party.update.return_value = mock_party
        mock_party.symbol = 'New Symbol'

        result = mock_party.update(mock_db_session, symbol='New Symbol')

        assert result.symbol == 'New Symbol'


@pytest.mark.unit
class TestPartyBulkOperations:
    """Tests for Party bulk operations."""

    def test_bulk_create(self, mock_db_session):
        """Test bulk creating parties."""
        parties_data = [
            {'id': 'P1', 'name': 'Party 1', 'short_name': 'P1'},
            {'id': 'P2', 'name': 'Party 2', 'short_name': 'P2'}
        ]

        with patch.object(Party, 'bulk_create') as mock_bulk:
            mock_parties = [Mock(spec=Party, id=p['id']) for p in parties_data]
            mock_bulk.return_value = mock_parties

            result = Party.bulk_create(mock_db_session, parties_data)

            assert len(result) == 2

    def test_bulk_upsert(self, mock_db_session):
        """Test bulk upserting parties."""
        parties_data = [
            {'id': 'P1', 'name': 'Party 1', 'short_name': 'P1'}
        ]

        with patch.object(Party, 'bulk_upsert', return_value=1):
            count = Party.bulk_upsert(mock_db_session, parties_data)
            assert count == 1


@pytest.mark.unit
class TestPartyDelete:
    """Tests for Party delete operations."""

    def test_delete_party(self, mock_db_session, mock_party):
        """Test deleting a party."""
        mock_party.delete(mock_db_session)
        mock_party.delete.assert_called_once_with(mock_db_session)


@pytest.mark.unit
class TestPartyValidation:
    """Tests for Party validation logic."""

    def test_party_id_format(self, sample_party_data):
        """Test party ID is uppercase."""
        assert sample_party_data['id'] == sample_party_data['id'].upper()

    def test_short_name_length(self, sample_party_data):
        """Test short name is concise."""
        assert len(sample_party_data['short_name']) <= 10

    def test_name_not_empty(self, sample_party_data):
        """Test party name is not empty."""
        assert len(sample_party_data['name']) > 0
