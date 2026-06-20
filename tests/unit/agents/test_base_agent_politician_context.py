"""BaseAgent politician context — primary sources only."""

from unittest.mock import MagicMock, patch

from app.agents.base_agent import BaseAgent


@patch("app.agents.base_agent.get_agent_llm")
def test_gather_politician_context_uses_field_citations(mock_llm_factory) -> None:
    mock_llm_factory.return_value = MagicMock()
    agent = BaseAgent()

    ctx = agent._gather_politician_context(
        {
            "name": "Example MLA",
            "state": "Kerala",
            "type": "MLA",
            "financial_disclosure": {
                "as_of_election": "Kerala 2021",
                "citation": {
                    "link": "https://myneta.info/Kerala2021/candidate.php?candidate_id=1",
                    "source": "MYNETA",
                },
            },
            "political_background": {
                "elections": [
                    {
                        "year": 2021,
                        "type": "MLA",
                        "state": "Kerala",
                        "constituency": "X",
                        "party": "Y",
                        "status": "WON",
                        "citation": {
                            "link": "https://results.eci.gov.in/example",
                            "source": "ECI",
                        },
                    }
                ]
            },
        }
    )

    assert "affidavit:" in ctx
    assert "election:" in ctx
    assert "Kerala 2021" in ctx
    assert "Wikipedia" not in ctx
    assert "Web Search" not in ctx


@patch("app.agents.base_agent.get_agent_llm")
def test_gather_politician_context_empty_without_citations(mock_llm_factory) -> None:
    mock_llm_factory.return_value = MagicMock()
    agent = BaseAgent()
    assert agent._gather_politician_context({"name": "X", "state": "Delhi", "type": "MP"}) == ""
