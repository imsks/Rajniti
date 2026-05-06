"""Politician schema and citation merge helpers."""

from app.agents.citation_audit_merge import (
    merge_citation_audit_updates,
    politician_needs_citation_audit,
)
from app.agents.politician_agent import _is_llm_quota_exc
from app.schemas.politician import CitationAuditLLMResult, Politician


def test_politician_accepts_citations() -> None:
    raw = {
        "id": "u1",
        "name": "Test",
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
                    "citation": {
                        "link": "https://results.eci.gov.in/example",
                        "source": "ECI",
                    },
                }
            ],
            "summary": "Short",
            "summary_citation": {
                "link": "https://example.com/summary",
                "source": "NEWS",
            },
        },
        "education": [
            {
                "qualification": "BACHELOR",
                "citation": {"link": "https://example.com/edu", "source": "GOV_WEBSITE"},
            }
        ],
        "contact_citations": {
            "email": {"link": "https://example.com/contact", "source": "GOV_WEBSITE"}
        },
    }
    p = Politician.model_validate(raw)
    assert p.political_background.elections[0].citation is not None
    assert p.political_background.summary_citation is not None


def test_politician_needs_citation_audit_missing() -> None:
    p = {
        "education": [{"qualification": "BACHELOR", "citation": None}],
        "political_background": {"elections": [], "summary": None},
    }
    assert politician_needs_citation_audit(p) is True


def test_merge_citation_audit_fills_education() -> None:
    politician = {
        "education": [{"qualification": "BACHELOR", "institution": "X"}],
        "political_background": {"elections": [], "summary": None},
    }
    audit = CitationAuditLLMResult(
        education_citations=[
            {"link": "https://example.com/a", "source": "ECI"},
        ]
    )
    updates, _ = merge_citation_audit_updates(politician, audit)
    assert "education" in updates
    assert updates["education"][0]["citation"]["source"] == "ECI"


def test_is_llm_quota_exc_matches_freetier_message() -> None:
    assert _is_llm_quota_exc(RuntimeError("FreeTierLLM: all candidates skipped or failed"))
    assert _is_llm_quota_exc(RuntimeError("RAJNITI_LLM_MAX_CALLS (5) exhausted for this run"))
    assert not _is_llm_quota_exc(ValueError("something else"))

