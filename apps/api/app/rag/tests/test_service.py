import pytest

from app.rag import RagQuery, RagResult, RagService


@pytest.mark.unit
def test_query_returns_result() -> None:
    result = RagService().query(RagQuery(text="water supply promises"))

    assert isinstance(result, RagResult)
    assert result.query == "water supply promises"
    assert result.answer is None


@pytest.mark.unit
def test_query_with_synthesis_delegates_to_agents() -> None:
    result = RagService().query(RagQuery(text="did they deliver?"), synthesize=True)

    assert result.answer is not None
    assert "rag_synthesis" in result.answer
