"""BaseAgent affidavit context tests."""

from unittest.mock import MagicMock, patch

from app.agents.base_agent import BaseAgent


@patch("app.agents.base_agent.get_agent_llm")
def test_gather_context_includes_affidavit_facts(mock_llm) -> None:
    mock_llm.return_value = MagicMock()
    agent = BaseAgent()

    politician = {
        "financial_disclosure": {
            "total_assets_inr": 1000000,
            "net_worth_inr": 900000,
            "as_of_election": "Bihar 2025",
            "citation": {
                "link": "https://www.myneta.info/Bihar2025/candidate.php?candidate_id=1",
                "source": "MYNETA",
            },
        },
        "education": [
            {
                "qualification": "BACHELOR",
                "institution": "Test College",
                "citation": {
                    "link": "https://www.myneta.info/Bihar2025/candidate.php?candidate_id=1",
                    "source": "MYNETA",
                },
            }
        ],
        "criminal_records": [
            {
                "name": "IPC 420",
                "type": "ECONOMIC",
                "citation": {
                    "link": "https://www.myneta.info/Bihar2025/candidate.php?candidate_id=1",
                    "source": "MYNETA",
                },
            }
        ],
        "political_background": {"elections": []},
    }

    context = agent._gather_politician_context(politician)

    assert "Affidavit facts" in context
    assert "total_assets_inr=1000000" in context
    assert "Test College" in context
    assert "IPC 420" in context
    assert "myneta.info" in context


@patch("app.agents.base_agent.get_agent_llm")
def test_format_affidavit_context_empty_when_no_data(mock_llm) -> None:
    mock_llm.return_value = MagicMock()
    agent = BaseAgent()
    assert agent._format_affidavit_context({}) == ""
