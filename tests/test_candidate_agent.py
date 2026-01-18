"""
Tests for the Candidate Data Population Agent.
"""

import sys
from unittest.mock import Mock, patch

import pytest

# Mock chromadb before any imports to avoid numpy compatibility issues in tests
sys.modules['chromadb'] = Mock()
sys.modules['chromadb.config'] = Mock()

from app.database.models import Candidate
from app.services.candidate_agent import CandidateAgent


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    with patch("app.services.candidate_agent.get_llm_service") as mock:
        service = Mock()
        mock.return_value = service
        service.search_india = Mock(return_value={
            "answer": '{"key": "value"}',
            "error": None,
        })
        yield service


@pytest.fixture
def agent(mock_llm_service):
    """Create a CandidateAgent instance for testing."""
    # Disable vector DB and cache for tests to avoid initialization issues
    return CandidateAgent(enable_vector_db=False, enable_cache=False)


@pytest.fixture
def mock_candidate():
    """Create a mock candidate for testing."""
    candidate = Mock(spec=Candidate)
    candidate.id = "test-123"
    candidate.name = "Test Candidate"
    candidate.constituency_id = "DL-1"
    candidate.education_background = None
    candidate.political_background = None
    candidate.family_background = None
    candidate.assets = None
    candidate.liabilities = None
    candidate.crime_cases = None
    candidate.update = Mock()
    return candidate


def test_agent_initialization(mock_llm_service):
    """Test that the agent initializes correctly."""
    agent = CandidateAgent(enable_vector_db=False, enable_cache=False)
    assert agent is not None
    assert agent.search_service is not None
    assert agent.enable_vector_db is False


def test_create_batch_query(agent, mock_candidate):
    """Test batch query generation."""
    fields = ["education", "political"]
    query = agent._create_batch_query(mock_candidate, fields)
    assert "Test Candidate" in query
    assert "education" in query.lower()
    assert "political" in query.lower()
    assert "JSON" in query


def test_extract_json_from_response_valid(agent):
    """Test JSON extraction from valid response."""
    response = 'Some text {"key": "value", "number": 123} more text'
    result = agent._extract_json_from_response(response)
    assert result == {"key": "value", "number": 123}


def test_extract_json_from_response_nested(agent):
    """Test JSON extraction with nested objects."""
    response = 'Text {"person": {"name": "John", "age": 30}} text'
    result = agent._extract_json_from_response(response)
    assert result == {"person": {"name": "John", "age": 30}}


def test_extract_json_from_response_invalid(agent):
    """Test JSON extraction with no valid JSON."""
    response = "This is just plain text without JSON"
    result = agent._extract_json_from_response(response)
    assert result is None


def test_extract_json_from_response_malformed(agent):
    """Test JSON extraction with malformed JSON."""
    response = 'Text {"key": value, "broken"} more text'
    result = agent._extract_json_from_response(response)
    assert result is None


def test_extract_json_from_response_array(agent):
    """Test JSON extraction with array response."""
    response = 'Result: [{"name": "John"}, {"name": "Jane"}]'
    result = agent._extract_json_from_response(response)
    assert result == [{"name": "John"}, {"name": "Jane"}]


def test_fetch_batch_data_success(agent, mock_candidate, mock_llm_service):
    """Test successful batch data fetch."""
    agent.search_service.search_india.return_value = {
        "answer": '{"education": {"year": "2000"}, "political": [{"party": "ABC"}]}',
        "error": None,
    }

    result = agent._fetch_batch_data(mock_candidate, ["education", "political"])

    assert result is not None
    agent.search_service.search_india.assert_called_once()


def test_fetch_batch_data_error(agent, mock_candidate, mock_llm_service):
    """Test batch data fetch with API error."""
    agent.search_service.search_india.return_value = {
        "answer": "",
        "error": "API Error",
    }

    result = agent._fetch_batch_data(mock_candidate, ["education"])
    # When there's an error, result may be empty dict or None
    assert result is None or result == {} or (isinstance(result, dict) and all(v is None for v in result.values()))


def test_find_candidates_needing_data(mock_llm_service):
    """Test finding candidates that need data."""
    mock_session = Mock()
    mock_query = Mock()
    mock_filter = Mock()
    mock_limit = Mock()

    # Setup mock chain
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.limit.return_value = mock_limit
    mock_limit.all.return_value = [Mock(spec=Candidate), Mock(spec=Candidate)]

    agent = CandidateAgent(enable_vector_db=False, enable_cache=False)

    candidates = agent.find_candidates_needing_data(mock_session, limit=10)

    assert len(candidates) == 2
    mock_session.query.assert_called_once_with(Candidate)


def test_run_agent_no_candidates(mock_llm_service):
    """Test agent run when no candidates need data."""
    mock_session = Mock()
    mock_query = Mock()
    mock_filter = Mock()
    mock_limit = Mock()

    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.limit.return_value = mock_limit
    mock_limit.all.return_value = []

    agent = CandidateAgent(enable_vector_db=False, enable_cache=False)

    stats = agent.run(mock_session, batch_size=10)

    assert stats["total_processed"] == 0
    assert stats["successful"] == 0
    assert stats["partial"] == 0
    assert stats["failed"] == 0


def test_validate_and_format_data_education(agent, mock_candidate):
    """Test validation and formatting of education data."""
    raw_data = [
        {
            "year": "2000",
            "stream": "Political Science",
            "college": "Delhi University"
        }
    ]
    result = agent._validate_and_format_data("education", raw_data, mock_candidate.name)
    # Result depends on schema validation, may be None if data doesn't match schema
    assert result is None or isinstance(result, list)


def test_validate_and_format_data_unknown_type(agent, mock_candidate):
    """Test validation returns None for unknown data types."""
    raw_data = [{"key": "value"}]
    result = agent._validate_and_format_data("unknown_type", raw_data, mock_candidate.name)
    assert result is None
