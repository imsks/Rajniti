"""
Tests for the Questions Service.
"""

import sys
from unittest.mock import Mock, patch, MagicMock
import pytest

# Mock chromadb before importing to avoid numpy compatibility issues in tests
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()

from app.schemas.questions import PREDEFINED_QUESTIONS
from app.services.questions_service import QuestionsService


@pytest.fixture
def mock_vector_db_service():
    """Mock VectorDBService for testing."""
    with patch("app.services.questions_service.VectorDBService") as mock:
        service = Mock()
        mock.return_value = service
        service.query_similar = Mock(return_value=[])
        yield service


@pytest.fixture
def questions_service(mock_vector_db_service):
    """Create a QuestionsService instance for testing."""
    return QuestionsService()


def test_predefined_questions_exist():
    """Test that predefined questions are defined."""
    assert len(PREDEFINED_QUESTIONS) == 3
    for q in PREDEFINED_QUESTIONS:
        assert "id" in q
        assert "question" in q
        assert "category" in q
        assert "description" in q


def test_predefined_questions_categories():
    """Test that predefined questions cover all categories."""
    categories = {q["category"] for q in PREDEFINED_QUESTIONS}
    expected_categories = {"criminal", "education", "assets"}
    assert categories == expected_categories


def test_get_predefined_questions(questions_service):
    """Test retrieving predefined questions."""
    questions = questions_service.get_predefined_questions()
    
    assert len(questions) == 3
    assert questions[0]["id"] == "q1"
    assert "criminal" in questions[0]["question"].lower()


def test_answer_question_no_results(questions_service, mock_vector_db_service):
    """Test answering a question with no results."""
    mock_vector_db_service.query_similar.return_value = []
    
    result = questions_service.answer_question("What is the education?")
    
    assert result["success"] is True
    assert "No relevant information found" in result["answer"]
    assert result["total_results"] == 0


def test_answer_question_with_results(questions_service, mock_vector_db_service):
    """Test answering a question with results."""
    mock_vector_db_service.query_similar.return_value = [
        {
            "id": "test-123",
            "document": "Name: Test Candidate. Party: BJP. Status: WON. Education: graduated in 2000 studied Political Science from Delhi University.",
            "metadata": {
                "candidate_id": "test-123",
                "name": "Test Candidate",
                "party_id": "BJP",
                "constituency_id": "DL-1",
                "state_id": "DL",
                "status": "WON",
            },
            "distance": 0.2,
        }
    ]
    
    result = questions_service.answer_question("What is the education background?")
    
    assert result["success"] is True
    assert result["total_results"] == 1
    assert len(result["candidates"]) == 1
    assert result["candidates"][0]["name"] == "Test Candidate"
    assert result["candidates"][0]["relevance_score"] == 0.8  # 1 - 0.2


def test_answer_question_with_candidate_filter(questions_service, mock_vector_db_service):
    """Test answering a question with candidate ID filter."""
    mock_vector_db_service.query_similar.return_value = [
        {
            "id": "test-123",
            "document": "Test document",
            "metadata": {"candidate_id": "test-123", "name": "Test Candidate"},
            "distance": 0.2,
        },
        {
            "id": "test-456",
            "document": "Another document",
            "metadata": {"candidate_id": "test-456", "name": "Another Candidate"},
            "distance": 0.3,
        },
    ]
    
    result = questions_service.answer_question(
        "What is the education?",
        candidate_id="test-123"
    )
    
    assert result["success"] is True
    assert result["total_results"] == 1
    assert result["candidates"][0]["candidate_id"] == "test-123"


def test_answer_predefined_question_success(questions_service, mock_vector_db_service):
    """Test answering a predefined question by ID."""
    mock_vector_db_service.query_similar.return_value = [
        {
            "id": "test-123",
            "document": "Name: Test. Crime cases: FIR 123/2020.",
            "metadata": {"candidate_id": "test-123", "name": "Test"},
            "distance": 0.1,
        }
    ]
    
    result = questions_service.answer_predefined_question("q1")
    
    assert result["success"] is True
    assert result["question_id"] == "q1"
    assert result["category"] == "criminal"


def test_answer_predefined_question_not_found(questions_service):
    """Test answering a predefined question with invalid ID."""
    result = questions_service.answer_predefined_question("invalid_id")
    
    assert result["success"] is False
    assert "not found" in result["error"]


def test_format_education_answer(questions_service):
    """Test formatting education-related answers."""
    results = [
        {
            "document": "Name: Test. Education: graduated in 2000 studied Political Science from Delhi University.",
            "metadata": {"name": "Test Candidate"},
        }
    ]
    
    answer = questions_service._format_education_answer(results)
    
    assert "Test Candidate" in answer
    assert "graduated in 2000" in answer


def test_format_political_answer(questions_service):
    """Test formatting political history answers."""
    results = [
        {
            "document": "Name: Test. Political History: In 2019 won from Delhi with BJP.",
            "metadata": {"name": "Test Candidate", "status": "WON", "party_id": "BJP"},
        }
    ]
    
    answer = questions_service._format_political_answer(results)
    
    assert "Test Candidate" in answer


def test_format_assets_answer(questions_service):
    """Test formatting assets-related answers."""
    results = [
        {
            "document": "Name: Test. Assets: Total assets: ₹1,000,000.00.",
            "metadata": {"name": "Test Candidate"},
        }
    ]
    
    answer = questions_service._format_assets_answer(results)
    
    assert "Test Candidate" in answer


def test_format_crime_answer(questions_service):
    """Test formatting criminal case answers."""
    results = [
        {
            "document": "Name: Test. Criminal Cases: 2 criminal case(s).",
            "metadata": {"name": "Test Candidate", "crime_cases_count": 2},
        }
    ]
    
    answer = questions_service._format_crime_answer(results)
    
    assert "Test Candidate" in answer
    assert "2 criminal case(s)" in answer


def test_format_family_answer(questions_service):
    """Test formatting family-related answers."""
    results = [
        {
            "document": "Name: Test. Family: Father Name (Father) is a Businessman.",
            "metadata": {"name": "Test Candidate"},
        }
    ]
    
    answer = questions_service._format_family_answer(results)
    
    assert "Test Candidate" in answer


def test_format_general_answer(questions_service):
    """Test formatting general answers."""
    results = [
        {
            "document": "Name: Test Candidate. Party: BJP. Status: WON.",
            "metadata": {"name": "Test Candidate", "party_id": "BJP", "status": "WON"},
        }
    ]
    
    answer = questions_service._format_general_answer(results)
    
    assert "Test Candidate" in answer
    assert "BJP" in answer
    assert "WON" in answer


def test_answer_question_handles_exception(questions_service, mock_vector_db_service):
    """Test that answer_question handles exceptions gracefully."""
    mock_vector_db_service.query_similar.side_effect = Exception("Database error")
    
    result = questions_service.answer_question("Test question")
    
    assert result["success"] is False
    assert "error" in result["answer"].lower()


def test_generate_answer_routes_correctly(questions_service):
    """Test that _generate_answer routes to correct formatter."""
    # Test education routing
    education_results = [
        {
            "document": "Name: Test. Education: graduated in 2000 studied Science.",
            "metadata": {"name": "Test"},
        }
    ]
    answer = questions_service._generate_answer("What is the education?", education_results)
    assert "Test" in answer
    
    # Test political routing
    political_results = [
        {
            "document": "Name: Test. Political History: won from Delhi.",
            "metadata": {"name": "Test", "status": "WON", "party_id": "BJP"},
        }
    ]
    answer = questions_service._generate_answer("What is the political history?", political_results)
    assert "Test" in answer
    
    # Test assets routing
    assets_results = [
        {
            "document": "Name: Test. Assets: Total assets: ₹1,000,000.",
            "metadata": {"name": "Test"},
        }
    ]
    answer = questions_service._generate_answer("What are the assets?", assets_results)
    assert "Test" in answer
    
    # Test crime routing
    crime_results = [
        {
            "document": "Name: Test. Criminal Cases: 1 criminal case(s).",
            "metadata": {"name": "Test", "crime_cases_count": 1},
        }
    ]
    answer = questions_service._generate_answer("Are there criminal cases?", crime_results)
    assert "Test" in answer
    
    # Test family routing
    family_results = [
        {
            "document": "Name: Test. Family: Father is a Teacher.",
            "metadata": {"name": "Test"},
        }
    ]
    answer = questions_service._generate_answer("What is the family background?", family_results)
    assert "Test" in answer
