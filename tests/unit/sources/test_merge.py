"""Unit tests for source merge precedence."""

from app.sources.base import SourceResult
from app.sources.merge import SOURCE_PRIORITY, merge_source_results


def _base():
    return {
        "id": "1",
        "name": "ECI Name",
        "state": "Bihar",
        "constituency": "AC",
        "type": "MLA",
        "education": [
            {
                "qualification": "BACHELOR",
                "institution": "LLM College",
                "citation": {"link": "https://news.example.com", "source": "NEWS"},
            }
        ],
        "criminal_records": [],
        "political_background": {
            "elections": [
                {
                    "year": 2025,
                    "type": "MLA",
                    "state": "Bihar",
                    "constituency": "AC",
                    "party": "BJP",
                    "status": "WON",
                    "citation": {"link": "https://eci.example.com", "source": "ECI"},
                }
            ],
        },
    }


def test_myneta_overwrites_llm_education_citations() -> None:
    myneta = SourceResult(
        source_name="myneta",
        priority=SOURCE_PRIORITY["myneta"],
        data={
            "education": [
                {
                    "qualification": "HIGH_SCHOOL",
                    "institution": "MyNeta School",
                    "citation": {
                        "link": "https://myneta.info/candidate.php?candidate_id=1",
                        "source": "MYNETA",
                    },
                }
            ],
            "financial_disclosure": {"total_assets_inr": 100},
        },
    )
    merged = merge_source_results(_base(), [myneta])
    assert merged["education"][0]["institution"] == "MyNeta School"
    assert merged["education"][0]["citation"]["source"] == "MYNETA"
    assert merged["financial_disclosure"]["total_assets_inr"] == 100


def test_eci_election_citation_not_downgraded() -> None:
    myneta = SourceResult(
        source_name="myneta",
        priority=SOURCE_PRIORITY["myneta"],
        data={
            "political_background": {
                "elections": [
                    {
                        "year": 2025,
                        "type": "MLA",
                        "state": "Bihar",
                        "constituency": "AC",
                        "party": "Other",
                        "status": "WON",
                        "citation": {
                            "link": "https://myneta.info/x",
                            "source": "MYNETA",
                        },
                    }
                ],
            },
        },
    )
    merged = merge_source_results(_base(), [myneta])
    # Existing ECI row kept when not prefer_incoming_elections from myneta priority
    assert merged["political_background"]["elections"][0]["party"] == "BJP"
    assert merged["political_background"]["elections"][0]["citation"]["source"] == "ECI"


def test_financial_disclosure_merge() -> None:
    myneta = SourceResult(
        source_name="myneta",
        priority=SOURCE_PRIORITY["myneta"],
        data={
            "financial_disclosure": {
                "total_assets_inr": 500,
                "citation": {
                    "link": "https://myneta.info/Bihar2025/candidate.php?candidate_id=9",
                    "source": "MYNETA",
                },
            },
            "source_sync": {"myneta": "2026-01-01T00:00:00Z"},
        },
    )
    merged = merge_source_results(_base(), [myneta])
    assert merged["financial_disclosure"]["total_assets_inr"] == 500
    assert merged["financial_disclosure"]["citation"]["source"] == "MYNETA"
    assert merged["source_sync"]["myneta"] == "2026-01-01T00:00:00Z"
