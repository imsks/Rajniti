"""Politician agent — skip enrichment when primary citations exist."""

from unittest.mock import MagicMock, patch

from app.agents.politician_agent import PoliticianCriminalRecords, PoliticianEducation


@patch("app.agents.base_agent.get_agent_llm")
def test_education_skips_when_primary_citation_present(mock_llm) -> None:
    mock_llm.return_value = MagicMock()
    proc = PoliticianEducation(MagicMock())
    politician = {
        "education": [
            {
                "qualification": "BACHELOR",
                "citation": {
                    "link": "https://example.com/affidavit",
                    "source": "MYNETA",
                },
            }
        ]
    }
    assert proc.should_run(politician, force=False) is False


@patch("app.agents.base_agent.get_agent_llm")
def test_criminal_records_skips_when_primary_citation_present(mock_llm) -> None:
    mock_llm.return_value = MagicMock()
    proc = PoliticianCriminalRecords(MagicMock())
    politician = {
        "criminal_records": [
            {
                "name": "IPC 420",
                "citation": {
                    "link": "https://example.com/affidavit",
                    "source": "GOV_WEBSITE",
                },
            }
        ]
    }
    assert proc.should_run(politician, force=False) is False
