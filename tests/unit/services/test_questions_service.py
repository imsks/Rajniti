"""
Unit tests for QuestionsService.

Tests cover predefined-question retrieval, free-form question answering,
predefined-question answer dispatch, and the internal _summarize helper.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb and fastembed before any app imports
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()
sys.modules["fastembed"] = MagicMock()

from app.schemas.questions import PREDEFINED_QUESTIONS  # noqa: E402
from app.services.questions_service import QuestionsService  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_vdb():
    vdb = Mock()
    vdb.count.return_value = 100
    vdb.search.return_value = []
    return vdb


@pytest.fixture
def questions_service(mock_vdb):
    """QuestionsService with an injected mock VectorDBService."""
    with patch("app.services.vector_db_service.VectorDBService") as MockVDB:
        MockVDB.return_value = mock_vdb
        svc = QuestionsService()
    # Replace with the fixture mock so tests can configure it directly
    svc.vdb = mock_vdb
    return svc


# ---------------------------------------------------------------------------
# get_predefined_questions()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetPredefinedQuestions:
    def test_returns_list_of_dicts(self, questions_service):
        result = questions_service.get_predefined_questions()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_returns_copy_not_original(self, questions_service):
        """Mutating the returned list must not affect PREDEFINED_QUESTIONS."""
        result = questions_service.get_predefined_questions()
        result.clear()
        assert len(PREDEFINED_QUESTIONS) > 0

    def test_each_question_has_required_keys(self, questions_service):
        for q in questions_service.get_predefined_questions():
            assert "id" in q
            assert "question" in q
            assert "category" in q


# ---------------------------------------------------------------------------
# answer_question()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAnswerQuestion:
    def test_returns_success_true_on_results(self, questions_service, mock_vdb):
        mock_vdb.search.return_value = [
            {
                "id": "mp-1",
                "document": "Name: Test MP. State: Delhi.",
                "metadata": {"name": "Test MP", "party": "BJP", "state": "Delhi"},
                "distance": 0.1,
            }
        ]
        result = questions_service.answer_question("criminal records")

        assert result["success"] is True
        assert result["total_results"] == 1
        assert result["politicians"][0]["name"] == "Test MP"

    def test_returns_no_results_message_when_empty(self, questions_service, mock_vdb):
        mock_vdb.search.return_value = []
        result = questions_service.answer_question("obscure query")

        assert result["success"] is True
        assert result["total_results"] == 0
        assert "No relevant" in result["answer"]

    def test_returns_success_false_on_exception(self, questions_service, mock_vdb):
        mock_vdb.search.side_effect = RuntimeError("db error")
        result = questions_service.answer_question("any question")

        assert result["success"] is False
        assert "db error" in result["answer"]

    def test_relevance_computed_from_distance(self, questions_service, mock_vdb):
        mock_vdb.search.return_value = [
            {
                "id": "p-1",
                "document": "doc",
                "metadata": {"name": "P1", "party": "", "state": ""},
                "distance": 0.25,
            }
        ]
        result = questions_service.answer_question("test")

        assert result["politicians"][0]["relevance"] == pytest.approx(0.75, abs=0.001)

    def test_snippet_truncated_at_300_chars(self, questions_service, mock_vdb):
        long_doc = "x" * 500
        mock_vdb.search.return_value = [
            {
                "id": "p-1",
                "document": long_doc,
                "metadata": {},
                "distance": 0.0,
            }
        ]
        result = questions_service.answer_question("test")

        snippet = result["politicians"][0]["snippet"]
        assert len(snippet) == 303  # 300 chars + "..."


# ---------------------------------------------------------------------------
# answer_predefined_question()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAnswerPredefinedQuestion:
    def test_valid_question_id_returns_answer(self, questions_service, mock_vdb):
        mock_vdb.search.return_value = []
        first_id = PREDEFINED_QUESTIONS[0]["id"]

        result = questions_service.answer_predefined_question(first_id)

        assert result["question_id"] == first_id

    def test_invalid_question_id_returns_error(self, questions_service):
        result = questions_service.answer_predefined_question("nonexistent")

        assert result["success"] is False
        assert "nonexistent" in result["error"]

    def test_category_included_in_result(self, questions_service, mock_vdb):
        mock_vdb.search.return_value = []
        q = PREDEFINED_QUESTIONS[0]

        result = questions_service.answer_predefined_question(q["id"])

        assert result["category"] == q["category"]


# ---------------------------------------------------------------------------
# _summarize()
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSummarize:
    def test_summarize_empty_results(self):
        assert QuestionsService._summarize("q", []) == "No relevant information found."

    def test_summarize_uses_top_three(self):
        results = [
            {"metadata": {"name": f"P{i}", "party": "BJP", "state": "DL"}}
            for i in range(5)
        ]
        summary = QuestionsService._summarize("query", results)

        assert "P0" in summary
        assert "P1" in summary
        assert "P2" in summary
        # Only top 3 should appear
        assert "P3" not in summary
        assert "P4" not in summary

    def test_summarize_formats_correctly(self):
        results = [{"metadata": {"name": "Modi", "party": "BJP", "state": "Gujarat"}}]
        summary = QuestionsService._summarize("leaders", results)

        assert "Modi" in summary
        assert "BJP" in summary
        assert "Gujarat" in summary
