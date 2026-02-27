"""
End-to-End tests for full user flows.

These tests simulate complete user journeys through the application,
testing multiple components working together.

NOTE: These tests are skipped by default as they require database setup.
Run with `pytest --run-e2e` to enable.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb before imports
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()

# Skip all E2E tests by default - they need database
pytestmark = pytest.mark.skip(
    reason="E2E tests require database setup. Run unit tests instead."
)


@pytest.fixture(autouse=True)
def mock_data_service():
    """Mock data_service at module level for all E2E tests."""
    with patch("app.services.data_service") as mock:
        # Setup default return values
        mock.get_elections.return_value = [
            {
                "id": "lok-sabha-2024",
                "name": "Lok Sabha 2024",
                "type": "LOK_SABHA",
                "year": 2024,
            }
        ]
        mock.get_election.return_value = None
        mock.get_candidates.return_value = []
        mock.search_candidates.return_value = []
        mock.get_candidate_by_id.return_value = None
        mock.get_candidate_by_id_only.return_value = None
        mock.get_election_statistics.return_value = {
            "total_candidates": 100,
            "total_constituencies": 50,
            "total_parties": 25,
            "total_winners": 50,
        }
        mock.get_party_seat_counts.return_value = [
            {"party_name": "BJP", "party_short_name": "BJP", "seats_won": 240}
        ]
        mock.enrich_candidate_data.side_effect = lambda c, e: c
        mock.get_all_parties.return_value = [
            {"id": "BJP", "name": "Bharatiya Janata Party", "short_name": "BJP"}
        ]
        mock.get_parties_by_election.return_value = [
            {"id": "BJP", "name": "Bharatiya Janata Party"}
        ]
        mock.get_all_constituencies.return_value = []
        mock.get_constituencies_by_election.return_value = []
        mock.get_constituency_by_id.return_value = None
        mock.get_state_name.return_value = "Delhi"
        yield mock


@pytest.mark.e2e
class TestUserOnboardingFlow:
    """Tests for user onboarding flow."""

    def test_complete_onboarding_flow(self, client, mock_data_service):
        """Test complete user onboarding flow."""
        # Step 1: User visits API root
        response = client.get("/api/v1/")
        assert response.status_code == 200
        data = response.get_json()
        assert "endpoints" in data

        # Step 2: User browses available elections
        response = client.get("/api/v1/elections")
        assert response.status_code == 200
        elections_data = response.get_json()
        assert elections_data["success"] is True


@pytest.mark.e2e
class TestCandidateSearchFlow:
    """Tests for candidate search flow."""

    def test_search_and_view_candidate_flow(self, client, mock_data_service):
        """Test searching and viewing a candidate."""
        # Setup mock for specific test
        mock_data_service.search_candidates.return_value = [
            {"id": "test-123", "name": "Test Candidate", "party_id": "BJP"}
        ]
        mock_data_service.get_candidate_by_id_only.return_value = {
            "id": "test-123",
            "name": "Test Candidate",
            "party_id": "BJP",
            "constituency_id": "DL-1",
        }

        # Step 1: Search for candidates
        response = client.get("/api/v1/candidates/search?q=Test")
        assert response.status_code == 200
        search_data = response.get_json()
        assert search_data["success"] is True

        # Step 2: View candidate details
        response = client.get("/api/v1/candidates/test-123")
        assert response.status_code == 200
        candidate_data = response.get_json()
        assert candidate_data["success"] is True


@pytest.mark.e2e
class TestElectionExplorationFlow:
    """Tests for election exploration flow."""

    def test_browse_elections_and_candidates_flow(self, client, mock_data_service):
        """Test browsing elections and candidates."""
        # Setup mocks
        mock_election = Mock()
        mock_election.name = "Lok Sabha 2024"
        mock_election.copy = Mock(
            return_value={
                "id": "lok-sabha-2024",
                "name": "Lok Sabha 2024",
                "type": "LOK_SABHA",
                "year": 2024,
            }
        )
        mock_data_service.get_election.return_value = mock_election
        mock_data_service.get_candidates.return_value = [
            {"id": "1", "name": "Candidate 1", "status": "WON"}
        ]

        # Step 1: Browse elections
        response = client.get("/api/v1/elections")
        assert response.status_code == 200

        # Step 2: View specific election
        response = client.get("/api/v1/elections/lok-sabha-2024")
        assert response.status_code == 200
        election_data = response.get_json()
        assert election_data["success"] is True

        # Step 3: View election candidates
        response = client.get("/api/v1/elections/lok-sabha-2024/candidates")
        assert response.status_code == 200


@pytest.mark.e2e
class TestPartyExplorationFlow:
    """Tests for party exploration flow."""

    def test_browse_parties_flow(self, client, mock_data_service):
        """Test browsing parties."""
        # Step 1: Get all parties
        response = client.get("/api/v1/parties")
        assert response.status_code == 200
        parties_data = response.get_json()
        assert parties_data["success"] is True

        # Step 2: Get parties for an election
        response = client.get("/api/v1/elections/lok-sabha-2024/parties")
        assert response.status_code in [200, 404]


@pytest.mark.e2e
class TestConstituencyExplorationFlow:
    """Tests for constituency exploration flow."""

    def test_browse_constituencies_flow(self, client, mock_data_service):
        """Test browsing constituencies."""
        mock_data_service.get_constituencies_by_election.return_value = [
            {"id": "DL-1", "name": "New Delhi", "state_id": "DL"}
        ]

        # Step 1: Get constituencies for an election
        response = client.get("/api/v1/elections/lok-sabha-2024/constituencies")
        assert response.status_code in [200, 404]

        # Step 2: Get constituencies by state
        mock_data_service.get_all_constituencies.return_value = [
            {"id": "DL-1", "name": "New Delhi", "state_id": "DL"}
        ]
        response = client.get("/api/v1/constituencies/by-state?state=Delhi")
        assert response.status_code == 200


@pytest.mark.e2e
class TestDataConsistencyFlow:
    """Tests for data consistency across endpoints."""

    def test_election_data_consistency(self, client, mock_data_service):
        """Test that election data is consistent across endpoints."""
        mock_election = Mock()
        mock_election.copy = Mock(
            return_value={
                "id": "lok-sabha-2024",
                "name": "Lok Sabha 2024",
                "type": "LOK_SABHA",
                "year": 2024,
            }
        )
        mock_data_service.get_election.return_value = mock_election

        # Get election from list
        response = client.get("/api/v1/elections")
        assert response.status_code == 200
        response.get_json()

        # Get same election by ID
        response = client.get("/api/v1/elections/lok-sabha-2024")
        assert response.status_code == 200
        election_detail = response.get_json()

        # Verify consistency
        assert election_detail["success"] is True
        assert election_detail["data"]["id"] == "lok-sabha-2024"


@pytest.mark.e2e
class TestConcurrentRequestsFlow:
    """Tests for handling multiple requests."""

    def test_multiple_endpoints_sequentially(self, client, mock_data_service):
        """Test accessing multiple endpoints in sequence."""
        endpoints = [
            "/api/v1/",
            "/api/v1/elections",
            "/api/v1/parties",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Failed for endpoint: {endpoint}"


@pytest.mark.e2e
class TestAPIDocumentation:
    """Tests for API documentation."""

    def test_documentation_completeness(self, client):
        """Test that API documentation is complete."""
        response = client.get("/api/v1/doc")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "endpoints" in data


@pytest.mark.e2e
class TestErrorHandling:
    """Tests for error handling across the application."""

    def test_404_for_nonexistent_election(self, client, mock_data_service):
        """Test 404 response for non-existent election."""
        mock_data_service.get_election.return_value = None

        response = client.get("/api/v1/elections/nonexistent-election")

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_404_for_nonexistent_candidate(self, client, mock_data_service):
        """Test 404 response for non-existent candidate."""
        mock_data_service.get_candidate_by_id_only.return_value = None

        response = client.get("/api/v1/candidates/nonexistent-candidate")

        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_search_empty_query(self, client, mock_data_service):
        """Test search with empty query."""
        mock_data_service.search_candidates.return_value = []

        response = client.get("/api/v1/candidates/search?q=")

        # Should return 200 with empty results or 400 for invalid query
        assert response.status_code in [200, 400]
