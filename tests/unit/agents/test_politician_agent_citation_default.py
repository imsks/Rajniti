"""PoliticianAgent default citation backfill tests."""

from unittest.mock import MagicMock, patch

import pytest

from app.agents.politician_agent import PoliticianAgent


@patch("app.agents.base_agent.get_agent_llm")
@pytest.mark.unit
def test_citation_agent_runs_by_default(mock_llm) -> None:
    mock_llm.return_value = MagicMock()
    agent = PoliticianAgent.__new__(PoliticianAgent)
    from app.agents.base_agent import BaseAgent

    BaseAgent.__init__(agent)

    politician = {
        "id": "test-id-1",
        "name": "Test",
        "political_background": {"elections": []},
    }
    agent.source_orchestrator = MagicMock()
    agent.politician_service = MagicMock()
    agent.politician_service.get_by_id.return_value = politician
    agent.citation_agent = MagicMock()
    agent.citation_agent._run_for_politician.return_value = {
        "ok": True,
        "updated_fields": ["social_media_citations"],
    }
    agent.cache = MagicMock()
    agent.cache.exists.return_value = True
    agent.processes = []

    result = agent._run_for_politician(
        politician,
        skip_sources=True,
        skip_citations=False,
    )

    agent.citation_agent._run_for_politician.assert_called_once()
    cite_steps = [r for r in result["process_results"] if r.get("process") == "citation_backfill"]
    assert len(cite_steps) == 1
    assert cite_steps[0]["ok"] is True


@patch("app.agents.base_agent.get_agent_llm")
@pytest.mark.unit
def test_skip_citations_skips_citation_agent(mock_llm) -> None:
    mock_llm.return_value = MagicMock()
    agent = PoliticianAgent.__new__(PoliticianAgent)
    from app.agents.base_agent import BaseAgent

    BaseAgent.__init__(agent)

    politician = {"id": "test-id-1", "name": "Test"}
    agent.source_orchestrator = MagicMock()
    agent.politician_service = MagicMock()
    agent.citation_agent = MagicMock()
    agent.cache = MagicMock()
    agent.cache.exists.return_value = True
    agent.processes = []

    agent._run_for_politician(
        politician,
        skip_sources=True,
        skip_citations=True,
    )

    agent.citation_agent._run_for_politician.assert_not_called()
