"""MyNeta source — validate-only path."""

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.sources import myneta as myneta_source

_CITATION = {
    "link": "https://www.myneta.info/Bihar2025/candidate.php?candidate_id=2927",
    "source": "MYNETA",
}


def _valid_payload(**overrides) -> dict:
    base = {
        "financial_disclosure": {
            "total_assets_inr": 23630189,
            "total_liabilities_inr": 0,
            "net_worth_inr": 23630189,
            "as_of_election": "Bihar 2025",
            "citation": _CITATION,
        },
        "education": [
            {
                "qualification": "BACHELOR",
                "institution": "Test College",
                "year_completed": 2010,
                "citation": _CITATION,
            }
        ],
        "criminal_records": [
            {"name": "IPC 420", "type": "ECONOMIC", "citation": _CITATION}
        ],
    }
    base.update(overrides)
    return base


def test_election_slug_for_bihar_mla() -> None:
    assert myneta_source.election_slug_for("MLA", "Bihar", year=2025) == "Bihar2025"


def test_validate_agent_result_accepts_schema_payload() -> None:
    import json

    validated = myneta_source.validate_agent_result(json.dumps(_valid_payload()))
    assert validated.financial_disclosure.total_assets_inr == 23630189
    assert validated.education[0].qualification.value == "BACHELOR"


def test_validate_agent_result_rejects_invalid_qualification() -> None:
    import json

    bad = _valid_payload()
    bad["education"][0]["qualification"] = "Graduate"
    with pytest.raises(ValidationError):
        myneta_source.validate_agent_result(json.dumps(bad))


def test_can_fetch_skips_when_synced() -> None:
    p = {
        "source_sync": {"myneta": "2026-01-01"},
        "financial_disclosure": {"citation": _CITATION},
        "state": "Bihar",
        "type": "MLA",
        "political_background": {"elections": []},
    }
    assert myneta_source.can_fetch(p, force=False) is False
    assert myneta_source.can_fetch(p, force=True) is True


def test_profile_url_from_financial_disclosure() -> None:
    p = {"financial_disclosure": {"citation": _CITATION}}
    assert myneta_source._profile_url(p) == _CITATION["link"]


def test_fetch_uses_browser_extract(monkeypatch) -> None:
    validated = myneta_source.MyNetaAgentResult.model_validate(_valid_payload())
    mock_extract = MagicMock(
        return_value=MagicMock(data=validated, steps_taken=5)
    )
    resolve_result = MagicMock(
        result=(
            '{"url":"https://www.myneta.info/Bihar2025/candidate.php?candidate_id=2927",'
            '"candidate_id":"2927","election_slug":"Bihar2025"}'
        )
    )
    mock_scrape = MagicMock(return_value=resolve_result)
    monkeypatch.setattr("app.browser.run_browser_extract", mock_extract)
    monkeypatch.setattr("app.browser.scraper.run_scrape_agent", mock_scrape)

    politician = {
        "name": "Test MLA",
        "state": "Bihar",
        "constituency": "AC",
        "type": "MLA",
        "political_background": {"elections": [{"year": 2025}]},
    }
    result = myneta_source.fetch(politician, force=True)
    mock_scrape.assert_called_once()
    mock_extract.assert_called_once()
    assert mock_extract.call_args.kwargs["output_model"].__name__ == "MyNetaBrowserExtract"
    assert result.data["financial_disclosure"]["total_assets_inr"] == 23630189
    assert result.data["source_sync"]["myneta"]
