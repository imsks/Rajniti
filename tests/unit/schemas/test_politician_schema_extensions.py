"""Schema extensions for source provenance and financial disclosure."""

import pytest

from app.schemas.politician import FinancialDisclosure, Politician


def _minimal_politician(**overrides):
    raw = {
        "id": "u1",
        "name": "Test Politician",
        "state": "Bihar",
        "constituency": "Test AC",
        "type": "MLA",
        "political_background": {
            "elections": [
                {
                    "year": 2025,
                    "type": "MLA",
                    "state": "Bihar",
                    "constituency": "Test AC",
                    "party": "X",
                    "status": "WON",
                }
            ],
        },
    }
    raw.update(overrides)
    return raw


def test_politician_backward_compat_without_new_fields() -> None:
    p = Politician.model_validate(_minimal_politician())
    assert p.financial_disclosure is None
    assert p.source_sync is None


def test_politician_accepts_financial_disclosure_with_citations() -> None:
    p = Politician.model_validate(
        _minimal_politician(
            financial_disclosure={
                "total_assets_inr": 23630189,
                "total_liabilities_inr": 0,
                "net_worth_inr": 23630189,
                "as_of_election": "Bihar 2025",
                "citation": {
                    "link": "https://www.myneta.info/Bihar2025/candidate.php?candidate_id=2927",
                    "source": "MYNETA",
                },
                "movable_assets": [
                    {
                        "description": "Cash",
                        "value_inr": 120000,
                        "citation": {
                            "link": "https://www.myneta.info/Bihar2025/candidate.php?candidate_id=2927",
                            "source": "MYNETA",
                        },
                    }
                ],
            },
            source_sync={"myneta": "2026-06-20T12:00:00Z"},
        )
    )
    assert p.financial_disclosure is not None
    assert p.financial_disclosure.total_assets_inr == 23630189
    assert p.financial_disclosure.citation is not None
    assert p.financial_disclosure.movable_assets[0].citation is not None
    assert p.source_sync == {"myneta": "2026-06-20T12:00:00Z"}


def test_financial_disclosure_model() -> None:
    fd = FinancialDisclosure(net_worth_inr=100)
    assert fd.total_assets_inr is None
