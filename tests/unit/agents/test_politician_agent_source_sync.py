"""PoliticianAgent source sync phase tests."""

from unittest.mock import MagicMock, patch

import pytest

from app.agents.politician_agent import PoliticianAgent


def _minimal_politician(**overrides) -> dict:
    base = {
        "id": "test-id-1",
        "name": "Test MLA",
        "state": "Bihar",
        "constituency": "AC",
        "type": "MLA",
        "political_background": {"elections": [{"year": 2025, "citation": {"link": "https://eci.example", "source": "ECI"}}]},
        "education": [{"qualification": "BACHELOR", "citation": {"link": "https://myneta.example", "source": "MYNETA"}}],
        "criminal_records": [],
        "social_media": {"twitter": "https://twitter.com/test", "citation": {"link": "https://news.example", "source": "NEWS"}},
        "family_background": [],
        "contact": {},
    }
    base.update(overrides)
    return base


@patch("app.agents.base_agent.get_agent_llm")
@pytest.mark.unit
def test_source_sync_runs_before_llm(mock_llm) -> None:
    mock_llm.return_value = MagicMock()
    agent = PoliticianAgent.__new__(PoliticianAgent)
    from app.agents.base_agent import BaseAgent

    BaseAgent.__init__(agent)

    politician = _minimal_politician()
    sync_mock = MagicMock(
        return_value={
            "id": "test-id-1",
            "ok": True,
            "sources_run": ["myneta"],
            "errors": [],
            "issues": [],
        }
    )
    agent.source_orchestrator = MagicMock()
    agent.source_orchestrator.sync_politician = sync_mock
    agent.politician_service = MagicMock()
    agent.politician_service.get_by_id.return_value = politician
    agent.citation_agent = MagicMock()
    agent.citation_agent._run_for_politician.return_value = {
        "ok": True,
        "skipped": True,
        "reason": "citations_complete",
    }
    agent.cache = MagicMock()
    agent.cache.exists.return_value = True
    agent.processes = []

    agent._run_for_politician(
        politician,
        force=False,
        source_names=["myneta"],
        skip_sources=False,
        skip_citations=False,
    )

    sync_mock.assert_called_once_with(
        politician,
        source_names=["myneta"],
        force=False,
    )
    agent.politician_service.get_by_id.assert_called()


@patch("app.agents.base_agent.get_agent_llm")
@pytest.mark.unit
def test_skip_sources_skips_orchestrator(mock_llm) -> None:
    mock_llm.return_value = MagicMock()
    agent = PoliticianAgent.__new__(PoliticianAgent)
    from app.agents.base_agent import BaseAgent

    BaseAgent.__init__(agent)

    politician = _minimal_politician()
    agent.source_orchestrator = MagicMock()
    agent.politician_service = MagicMock()
    agent.politician_service.get_by_id.return_value = politician
    agent.citation_agent = MagicMock()
    agent.citation_agent._run_for_politician.return_value = {"ok": True, "skipped": True}
    agent.cache = MagicMock()
    agent.cache.exists.return_value = True
    agent.processes = []

    agent._run_for_politician(
        politician,
        skip_sources=True,
        skip_citations=True,
    )

    agent.source_orchestrator.sync_politician.assert_not_called()
