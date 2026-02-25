"""
Shared pytest fixtures for Rajniti test suite.

This file provides common test fixtures used across unit, integration, and E2E tests.
Fixtures are organized by scope and purpose for optimal test isolation and performance.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb before any imports to avoid numpy compatibility issues
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()

# Set test environment
os.environ["FLASK_ENV"] = "testing"
os.environ["TESTING"] = "true"


# =============================================================================
# Application Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def app():
    """
    Create Flask application for testing.
    Session-scoped for efficiency across all tests.
    """
    # Import here after environment setup
    from app import create_app

    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "WTF_CSRF_ENABLED": False,
        }
    )

    yield app


@pytest.fixture(scope="function")
def client(app):
    """
    Create test client for making HTTP requests.
    Function-scoped for test isolation.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def app_context(app):
    """
    Create application context for tests that need it.
    """
    with app.app_context():
        yield app


# =============================================================================
# Database Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def mock_db_session():
    """
    Create a mock database session for unit tests.
    Provides complete isolation without actual database access.
    """
    session = Mock()
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.flush = Mock()
    session.close = Mock()
    session.delete = Mock()

    # Setup default query chain behavior
    mock_query = Mock()
    mock_query.filter = Mock(return_value=mock_query)
    mock_query.filter_by = Mock(return_value=mock_query)
    mock_query.first = Mock(return_value=None)
    mock_query.all = Mock(return_value=[])
    mock_query.count = Mock(return_value=0)
    mock_query.offset = Mock(return_value=mock_query)
    mock_query.limit = Mock(return_value=mock_query)
    mock_query.order_by = Mock(return_value=mock_query)
    session.query.return_value = mock_query

    yield session


@pytest.fixture(scope="function")
def mock_get_db_session(mock_db_session):
    """
    Patch the get_db_session context manager for tests.
    """

    class MockContextManager:
        def __enter__(self):
            return mock_db_session

        def __exit__(self, *args):
            pass

    with patch("app.database.get_db_session", return_value=MockContextManager()):
        yield mock_db_session


# =============================================================================
# Model Fixtures
# =============================================================================


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "username": "testuser",
        "profile_picture": "https://example.com/picture.jpg",
        "state": "DL",
        "city": "Delhi",
        "pincode": "110001",
        "age_group": "25-35",
        "political_ideology": "Neutral",
        "onboarding_completed": False,
    }


@pytest.fixture
def sample_candidate_data() -> Dict[str, Any]:
    """Sample candidate data for testing (JSON format)."""
    return {
        "id": "test-candidate-123",
        "name": "Test Candidate",
        "party_id": "BJP",
        "constituency_id": "DL-1",
        "state_id": "DL",
        "status": "WON",
        "type": "MLA",
        "image_url": "https://example.com/candidate.jpg",
        "education_background": [
            {
                "year": "2000",
                "college": "Delhi University",
                "stream": "Political Science",
            }
        ],
        "political_background": [
            {
                "election_year": "2019",
                "party": "BJP",
                "result": "WON",
                "constituency": "Delhi-1",
            }
        ],
        "family_background": [
            {"name": "Father Name", "relation": "Father", "profession": "Businessman"}
        ],
        "assets": [
            {
                "type": "CASH",
                "amount": 1000000.0,
                "description": "Cash in hand",
                "owned_by": "SELF",
            }
        ],
        "liabilities": [
            {
                "type": "LOAN",
                "amount": 500000.0,
                "description": "Home loan",
                "owned_by": "SELF",
            }
        ],
        "crime_cases": [
            {"fir_no": "123", "charges_framed": False, "description": "Pending case"}
        ],
    }


@pytest.fixture
def sample_election_data() -> Dict[str, Any]:
    """Sample election data for testing (JSON format)."""
    return {
        "id": "lok-sabha-2024",
        "name": "Lok Sabha Elections 2024",
        "type": "LOK_SABHA",
        "year": 2024,
        "total_constituencies": 543,
        "total_candidates": 8000,
        "total_parties": 450,
        "result_status": "DECLARED",
    }


@pytest.fixture
def sample_party_data() -> Dict[str, Any]:
    """Sample party data for testing (JSON format)."""
    return {
        "id": "BJP",
        "name": "Bharatiya Janata Party",
        "short_name": "BJP",
        "symbol": "Lotus",
    }


@pytest.fixture
def sample_constituency_data() -> Dict[str, Any]:
    """Sample constituency data for testing (JSON format)."""
    return {
        "id": "DL-1",
        "name": "New Delhi",
        "state_id": "DL",
    }


# =============================================================================
# Mock Model Fixtures
# =============================================================================


@pytest.fixture
def mock_user(sample_user_data):
    """Create a mock User model instance."""
    from app.database.models import User

    user = Mock(spec=User)
    for key, value in sample_user_data.items():
        setattr(user, key, value)
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    user.to_dict = Mock(return_value=sample_user_data)
    user.update = Mock(return_value=user)
    user.delete = Mock()
    return user


# =============================================================================
# Service Mocks
# =============================================================================


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    with patch("app.services.candidate_agent.get_llm_service") as mock:
        service = Mock()
        mock.return_value = service
        service.search_india = Mock(
            return_value={
                "answer": '{"education": [], "political": [], "family": [], "assets": [], "liabilities": [], "crime_cases": []}',
                "error": None,
            }
        )
        yield service


@pytest.fixture
def mock_vector_db_service():
    """Mock VectorDBService for testing."""
    with patch("app.services.questions_service.VectorDBService") as mock:
        service = Mock()
        mock.return_value = service
        service.query_similar = Mock(return_value=[])
        service.upsert_candidate_data = Mock()
        service.delete_candidate = Mock()
        service.count_candidates = Mock(return_value=100)
        yield service


# =============================================================================
# API Response Helpers
# =============================================================================


@pytest.fixture
def assert_api_success():
    """Helper to assert successful API responses."""

    def _assert(response, expected_data=None):
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        if expected_data:
            assert data["data"] == expected_data
        return data

    return _assert


@pytest.fixture
def assert_api_error():
    """Helper to assert error API responses."""

    def _assert(response, expected_status=400, expected_error=None):
        assert response.status_code == expected_status
        data = response.get_json()
        assert data["success"] is False
        if expected_error:
            assert expected_error in data.get("error", "")
        return data

    return _assert


# =============================================================================
# Test Data Generators
# =============================================================================


@pytest.fixture
def generate_users(sample_user_data):
    """Generate multiple user fixtures."""

    def _generate(count: int = 5):
        users = []
        for i in range(count):
            user_data = sample_user_data.copy()
            user_data["id"] = f"user-{i}"
            user_data["email"] = f"user{i}@example.com"
            user_data["username"] = f"user{i}"
            users.append(user_data)
        return users

    return _generate


@pytest.fixture
def generate_candidates(sample_candidate_data):
    """Generate multiple candidate fixtures (JSON format)."""

    def _generate(count: int = 5):
        candidates = []
        for i in range(count):
            candidate_data = sample_candidate_data.copy()
            candidate_data["id"] = f"candidate-{i}"
            candidate_data["name"] = f"Candidate {i}"
            candidate_data["constituency_id"] = f"DL-{i}"
            candidates.append(candidate_data)
        return candidates

    return _generate


# =============================================================================
# Environment Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def production_env():
    """Set production environment variables."""
    os.environ["FLASK_ENV"] = "production"
    os.environ["TESTING"] = "false"
    yield
    os.environ["FLASK_ENV"] = "testing"
    os.environ["TESTING"] = "true"


@pytest.fixture
def development_env():
    """Set development environment variables."""
    os.environ["FLASK_ENV"] = "development"
    os.environ["TESTING"] = "false"
    yield
    os.environ["FLASK_ENV"] = "testing"
    os.environ["TESTING"] = "true"


# =============================================================================
# Cleanup Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def cleanup_mocks():
    """Clean up any lingering mocks after each test."""
    yield
    # Reset any module-level mocks if needed


# =============================================================================
# Markers
# =============================================================================


def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line(
        "markers", "integration: Integration tests (may use real services)"
    )
    config.addinivalue_line("markers", "e2e: End-to-end tests (full system tests)")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "database: Tests requiring database")
    config.addinivalue_line("markers", "external: Tests requiring external services")
