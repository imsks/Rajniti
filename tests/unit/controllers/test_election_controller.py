"""
Unit tests for ElectionController.

Tests cover election retrieval and statistics operations.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb before imports
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()


@pytest.fixture(autouse=True)
def mock_data_service():
    """Mock the data_service at the module level."""
    with patch('app.services.data_service') as mock:
        # Also patch the import in controllers module
        with patch('app.controllers.election_controller.data_service', mock):
            yield mock


@pytest.fixture
def election_controller(mock_data_service):
    """Create an ElectionController instance with mocked data service."""
    from app.controllers.election_controller import ElectionController
    controller = ElectionController()
    controller.data_service = mock_data_service
    return controller


@pytest.mark.unit
class TestGetAllElections:
    """Tests for get_all_elections method."""

    def test_get_all_empty(self, election_controller, mock_data_service):
        """Test getting elections when none exist."""
        mock_data_service.get_elections.return_value = []

        result = election_controller.get_all_elections()

        assert result == []

    def test_get_all_with_elections(self, election_controller, mock_data_service, sample_election_data):
        """Test getting all elections with statistics."""
        mock_data_service.get_elections.return_value = [sample_election_data]
        mock_data_service.get_election_statistics.return_value = {
            'total_candidates': 100,
            'total_constituencies': 50,
            'total_parties': 25,
            'total_winners': 50
        }

        result = election_controller.get_all_elections()

        assert len(result) == 1
        assert result[0]['id'] == sample_election_data['id']
        assert 'statistics' in result[0]
        assert result[0]['statistics']['total_candidates'] == 100

    def test_get_all_multiple_elections(self, election_controller, mock_data_service):
        """Test getting multiple elections."""
        elections = [
            {'id': 'election-1', 'name': 'Election 1', 'type': 'LOK_SABHA', 'year': 2024},
            {'id': 'election-2', 'name': 'Election 2', 'type': 'VIDHAN_SABHA', 'year': 2024}
        ]
        mock_data_service.get_elections.return_value = elections
        mock_data_service.get_election_statistics.return_value = {
            'total_candidates': 50,
            'total_constituencies': 25,
            'total_parties': 10,
            'total_winners': 25
        }

        result = election_controller.get_all_elections()

        assert len(result) == 2
        assert mock_data_service.get_election_statistics.call_count == 2


@pytest.mark.unit
class TestGetElectionById:
    """Tests for get_election_by_id method."""

    def test_election_not_found(self, election_controller, mock_data_service):
        """Test getting election when not found."""
        mock_data_service.get_election.return_value = None

        result = election_controller.get_election_by_id('nonexistent')

        assert result is None

    def test_election_found_with_statistics(self, election_controller, mock_data_service, sample_election_data):
        """Test getting election with full statistics."""
        mock_election = Mock()
        mock_election.copy = Mock(return_value=sample_election_data.copy())
        mock_data_service.get_election.return_value = mock_election
        
        mock_data_service.get_election_statistics.return_value = {
            'total_candidates': 8000,
            'total_constituencies': 543,
            'total_parties': 450,
            'total_winners': 543
        }
        
        mock_data_service.get_party_seat_counts.return_value = [
            {'party_name': 'BJP', 'party_short_name': 'BJP', 'seats_won': 240},
            {'party_name': 'INC', 'party_short_name': 'INC', 'seats_won': 99}
        ]

        result = election_controller.get_election_by_id('lok-sabha-2024')

        assert result is not None
        assert result['id'] == sample_election_data['id']
        assert 'statistics' in result
        assert result['statistics']['total_candidates'] == 8000
        assert 'top_parties' in result['statistics']
        assert len(result['statistics']['top_parties']) == 2

    def test_election_top_parties_limit(self, election_controller, mock_data_service, sample_election_data):
        """Test that top parties are limited to 5."""
        mock_election = Mock()
        mock_election.copy = Mock(return_value=sample_election_data.copy())
        mock_data_service.get_election.return_value = mock_election
        
        mock_data_service.get_election_statistics.return_value = {
            'total_candidates': 100,
            'total_constituencies': 50,
            'total_parties': 25,
            'total_winners': 50
        }
        
        # Return 5 parties (the limit)
        mock_data_service.get_party_seat_counts.return_value = [
            {'party_name': f'Party {i}', 'party_short_name': f'P{i}', 'seats_won': 10 - i}
            for i in range(5)
        ]

        result = election_controller.get_election_by_id('lok-sabha-2024')

        # get_party_seat_counts should be called with limit=5
        mock_data_service.get_party_seat_counts.assert_called_once_with('lok-sabha-2024', limit=5)


@pytest.mark.unit
class TestElectionControllerEdgeCases:
    """Tests for edge cases and error scenarios."""

    def test_statistics_with_zero_values(self, election_controller, mock_data_service, sample_election_data):
        """Test handling elections with zero statistics."""
        mock_election = Mock()
        mock_election.copy = Mock(return_value=sample_election_data.copy())
        mock_data_service.get_election.return_value = mock_election
        
        mock_data_service.get_election_statistics.return_value = {
            'total_candidates': 0,
            'total_constituencies': 0,
            'total_parties': 0,
            'total_winners': 0
        }
        mock_data_service.get_party_seat_counts.return_value = []

        result = election_controller.get_election_by_id('empty-election')

        assert result['statistics']['total_candidates'] == 0
        assert result['statistics']['top_parties'] == []

    def test_elections_empty_statistics(self, election_controller, mock_data_service):
        """Test elections list with empty statistics."""
        mock_data_service.get_elections.return_value = [
            {'id': 'new-election', 'name': 'New', 'type': 'LOK_SABHA', 'year': 2025}
        ]
        mock_data_service.get_election_statistics.return_value = {}

        result = election_controller.get_all_elections()

        assert len(result) == 1
        assert 'statistics' in result[0]

    def test_data_service_initialization(self, election_controller):
        """Test that controller properly initializes data service."""
        assert election_controller.data_service is not None

    def test_election_copy_maintains_original(self, election_controller, mock_data_service, sample_election_data):
        """Test that getting election doesn't modify original data."""
        original_copy = sample_election_data.copy()
        mock_election = Mock()
        mock_election.copy = Mock(return_value=sample_election_data.copy())
        mock_data_service.get_election.return_value = mock_election
        mock_data_service.get_election_statistics.return_value = {'total_candidates': 100}
        mock_data_service.get_party_seat_counts.return_value = []

        election_controller.get_election_by_id('lok-sabha-2024')

        # Original data should not have statistics added
        assert 'statistics' not in original_copy or original_copy.get('statistics') != {'total_candidates': 100}
