"""BaseAgent politician context aggregation."""

from unittest.mock import MagicMock, patch

from app.agents.base_agent import BaseAgent


@patch("app.agents.base_agent.get_agent_llm")
def test_gather_politician_context_has_structured_wikipedia(mock_llm_factory) -> None:
    mock_llm_factory.return_value = MagicMock()
    agent = BaseAgent()
    wm = MagicMock()
    wm.politician_wikipedia_bundle.return_value = {
        "title": "Example MLA",
        "article_url": "https://en.wikipedia.org/wiki/Example_MLA",
        "extract": "Example MLA served in Vidhan Sabha.",
        "external_links": ["https://eci.gov.in/result/sample"],
    }
    ws = MagicMock()
    ws.search_text.return_value = "snippet line"
    agent._tools = {
        "wikipedia": wm,
        "web_search": ws,
        "web_scraper": MagicMock(),
    }

    ctx = agent._gather_politician_context(
        {"name": "Example MLA", "state": "Kerala", "type": "MLA"}
    )

    assert "Article URL: https://en.wikipedia.org/wiki/Example_MLA" in ctx
    assert "Outbound links" in ctx
    assert "https://eci.gov.in/result/sample" in ctx
    assert "Web Search Results" in ctx
    wm.politician_wikipedia_bundle.assert_called_once_with("Example MLA", "Kerala")


@patch("app.agents.base_agent.get_agent_llm")
def test_gather_fallback_plain_wikipedia_when_no_extract(mock_llm_factory) -> None:
    mock_llm_factory.return_value = MagicMock()
    agent = BaseAgent()
    wm = MagicMock()
    wm.politician_wikipedia_bundle.return_value = {}

    ws = MagicMock()
    ws.search_text.return_value = ""
    agent._tools = {
        "wikipedia": wm,
        "web_search": ws,
        "web_scraper": MagicMock(),
    }

    agent._search_wikipedia = MagicMock(return_value="plain wiki body")

    ctx = agent._gather_politician_context(
        {"name": "X", "state": "Delhi", "type": "MP"}
    )

    assert "=== Wikipedia ===" in ctx
    assert "plain wiki body" in ctx
    agent._search_wikipedia.assert_called_once()
