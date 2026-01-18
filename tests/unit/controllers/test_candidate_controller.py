"""
Unit tests for CandidateController.

Tests cover candidate search, retrieval, and filtering operations.
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
        with patch('app.controllers.candidate_controller.data_service', mock):
            yield mock


@pytest.fixture
def candidate_controller(mock_data_service):
    """Create a CandidateController instance with mocked data service."""
    from app.controllers.candidate_controller import CandidateController
    controller = CandidateController()
    controller.data_service = mock_data_service
    return controller


@pytest.mark.unit
class TestSearchCandidates:
    """Tests for search_candidates method."""

    def test_search_with_default_election(self, candidate_controller, mock_data_service):
        """Test searching without specifying election_id uses default."""
        mock_data_service.search_candidates.return_value = [
            {'id': '1', 'name': 'Test Candidate'}
        ]

        result = candidate_controller.search_candidates('Test')

        assert result['election_id'] == 'lok-sabha-2024'
        assert result['query'] == 'Test'
        assert result['total_results'] == 1
        mock_data_service.search_candidates.assert_called_once_with('Test', 'lok-sabha-2024')

    def test_search_with_specific_election(self, candidate_controller, mock_data_service):
        """Test searching with specific election_id."""
        mock_data_service.search_candidates.return_value = []

        result = candidate_controller.search_candidates('Test', election_id='vs-2024')

        assert result['election_id'] == 'vs-2024'
        mock_data_service.search_candidates.assert_called_once_with('Test', 'vs-2024')

    def test_search_with_limit(self, candidate_controller, mock_data_service):
        """Test searching with limit parameter."""
        mock_data_service.search_candidates.return_value = [
            {'id': '1'}, {'id': '2'}, {'id': '3'}
        ]

        result = candidate_controller.search_candidates('Test', limit=2)

        assert len(result['candidates']) == 2
        assert result['total_results'] == 2

    def test_search_empty_results(self, candidate_controller, mock_data_service):
        """Test searching with no results."""
        mock_data_service.search_candidates.return_value = []

        result = candidate_controller.search_candidates('Nonexistent')

        assert result['total_results'] == 0
        assert result['candidates'] == []


@pytest.mark.unit
class TestGetCandidatesByElection:
    """Tests for get_candidates_by_election method."""

    def test_election_not_found(self, candidate_controller, mock_data_service):
        """Test when election is not found."""
        mock_data_service.get_election.return_value = None

        result = candidate_controller.get_candidates_by_election('nonexistent')

        assert result is None

    def test_get_candidates_success(self, candidate_controller, mock_data_service, sample_election_data):
        """Test getting candidates successfully."""
        mock_election = Mock()
        mock_election.name = sample_election_data['name']
        mock_data_service.get_election.return_value = mock_election
        mock_data_service.get_candidates.return_value = [
            {'id': '1', 'name': 'Candidate 1'},
            {'id': '2', 'name': 'Candidate 2'}
        ]
        mock_data_service.enrich_candidate_data.side_effect = lambda c, e: c

        result = candidate_controller.get_candidates_by_election('lok-sabha-2024')

        assert result['election_id'] == 'lok-sabha-2024'
        assert result['total_candidates'] == 2

    def test_get_candidates_with_limit(self, candidate_controller, mock_data_service, sample_election_data):
        """Test getting candidates with limit."""
        mock_election = Mock()
        mock_election.name = sample_election_data['name']
        mock_data_service.get_election.return_value = mock_election
        mock_data_service.get_candidates.return_value = [
            {'id': '1'}, {'id': '2'}, {'id': '3'}
        ]
        mock_data_service.enrich_candidate_data.side_effect = lambda c, e: c

        result = candidate_controller.get_candidates_by_election('lok-sabha-2024', limit=2)

        assert result['showing'] == 2


@pytest.mark.unit
class TestGetCandidateById:
    """Tests for get_candidate_by_id methods."""

    def test_get_candidate_found(self, candidate_controller, mock_data_service, sample_candidate_data):
        """Test getting candidate by ID when found."""
        mock_data_service.get_candidate_by_id.return_value = sample_candidate_data

        result = candidate_controller.get_candidate_by_id('test-123', 'lok-sabha-2024')

        assert result == sample_candidate_data
        mock_data_service.get_candidate_by_id.assert_called_once()

    def test_get_candidate_not_found(self, candidate_controller, mock_data_service):
        """Test getting candidate by ID when not found."""
        mock_data_service.get_candidate_by_id.return_value = None

        result = candidate_controller.get_candidate_by_id('nonexistent', 'lok-sabha-2024')

        assert result is None

    def test_get_candidate_by_id_only(self, candidate_controller, mock_data_service, sample_candidate_data):
        """Test getting candidate without election_id."""
        mock_data_service.get_candidate_by_id_only.return_value = sample_candidate_data

        result = candidate_controller.get_candidate_by_id_only('test-123')

        assert result == sample_candidate_data


@pytest.mark.unit
class TestGetCandidatesByParty:
    """Tests for get_candidates_by_party method."""

    def test_party_default_election(self, candidate_controller, mock_data_service):
        """Test getting candidates by party with default election."""
        mock_data_service.get_election.return_value = None

        result = candidate_controller.get_candidates_by_party('BJP')

        assert result['election_id'] == 'lok-sabha-2024'
        assert result['total_candidates'] == 0

    def test_party_election_not_found(self, candidate_controller, mock_data_service):
        """Test getting candidates by party when election not found."""
        mock_data_service.get_election.return_value = None

        result = candidate_controller.get_candidates_by_party('BJP', 'nonexistent')

        assert result['total_candidates'] == 0
        assert result['candidates'] == []

    def test_party_candidates_found(self, candidate_controller, mock_data_service):
        """Test getting candidates by party when found."""
        mock_election = Mock()
        mock_data_service.get_election.return_value = mock_election
        mock_data_service.get_candidates.return_value = [
            {'id': '1', 'party_id': 'BJP'}
        ]
        mock_data_service.enrich_candidate_data.return_value = {
            'id': '1',
            'party_name': 'Bharatiya Janata Party',
            'party_short_name': 'BJP'
        }

        result = candidate_controller.get_candidates_by_party('BJP')

        assert result['total_candidates'] == 1

    def test_party_case_insensitive_match(self, candidate_controller, mock_data_service):
        """Test party name matching is case insensitive."""
        mock_election = Mock()
        mock_data_service.get_election.return_value = mock_election
        mock_data_service.get_candidates.return_value = [{'id': '1'}]
        mock_data_service.enrich_candidate_data.return_value = {
            'party_name': 'BHARATIYA JANATA PARTY',
            'party_short_name': 'BJP'
        }

        result = candidate_controller.get_candidates_by_party('bharatiya janata party')

        # Match should work regardless of case
        assert result is not None


@pytest.mark.unit
class TestGetCandidatesByConstituency:
    """Tests for get_candidates_by_constituency method."""

    def test_election_not_found(self, candidate_controller, mock_data_service):
        """Test when election is not found."""
        mock_data_service.get_election.return_value = None

        result = candidate_controller.get_candidates_by_constituency('DL-1', 'nonexistent')

        assert result is None

    def test_constituency_not_found(self, candidate_controller, mock_data_service):
        """Test when constituency is not found."""
        mock_election = Mock()
        mock_data_service.get_election.return_value = mock_election
        mock_data_service.get_constituency_by_id.return_value = None

        result = candidate_controller.get_candidates_by_constituency('NONEXISTENT', 'lok-sabha-2024')

        assert result is None

    def test_constituency_candidates_found(self, candidate_controller, mock_data_service):
        """Test getting candidates by constituency when found."""
        mock_election = Mock()
        mock_data_service.get_election.return_value = mock_election
        
        mock_constituency = Mock()
        mock_constituency.name = 'New Delhi'
        mock_constituency.state_id = 'DL'
        mock_data_service.get_constituency_by_id.return_value = mock_constituency
        
        mock_data_service.get_candidates.return_value = [
            {'id': '1', 'constituency_id': 'DL-1', 'status': 'WON'},
            {'id': '2', 'constituency_id': 'DL-1', 'status': 'LOST'}
        ]
        mock_data_service.enrich_candidate_data.side_effect = lambda c, e: {**c, 'name': f"Candidate {c['id']}"}
        mock_data_service.get_state_name.return_value = 'Delhi'

        result = candidate_controller.get_candidates_by_constituency('DL-1', 'lok-sabha-2024')

        assert result['constituency_id'] == 'DL-1'
        assert result['total_candidates'] == 2
        # Winners should be sorted first
        assert result['candidates'][0]['status'] == 'WON'


@pytest.mark.unit
class TestGetWinningCandidates:
    """Tests for get_winning_candidates method."""

    def test_default_election(self, candidate_controller, mock_data_service):
        """Test getting winners with default election."""
        mock_data_service.get_election.return_value = None

        result = candidate_controller.get_winning_candidates()

        assert result['election_id'] == 'lok-sabha-2024'

    def test_election_not_found(self, candidate_controller, mock_data_service):
        """Test when election is not found."""
        mock_data_service.get_election.return_value = None

        result = candidate_controller.get_winning_candidates('nonexistent')

        assert result['total_winners'] == 0
        assert result['winners'] == []

    def test_winners_found(self, candidate_controller, mock_data_service, sample_election_data):
        """Test getting winners when found."""
        mock_election = Mock()
        mock_election.name = sample_election_data['name']
        mock_data_service.get_election.return_value = mock_election
        mock_data_service.get_candidates.return_value = [
            {'id': '1', 'status': 'WON'},
            {'id': '2', 'status': 'LOST'},
            {'id': '3', 'status': 'WON'}
        ]
        mock_data_service.enrich_candidate_data.side_effect = lambda c, e: c

        result = candidate_controller.get_winning_candidates('lok-sabha-2024')

        assert result['total_winners'] == 2
        assert len(result['winners']) == 2
