"""Politician schema and citation merge helpers."""

import pytest

from app.agents.citation_audit_merge import (
    CITATION_COVERAGE_SKIP_THRESHOLD_PCT,
    merge_citation_audit_updates,
    politician_citation_coverage_pct,
    politician_citation_coverage_summary,
    politician_citation_gaps,
    politician_needs_citation_audit,
)
from app.agents.politician_agent import _is_llm_quota_exc
from app.prompts.politician_prompts import PoliticianPrompts
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
                "citation": {
                    "link": "https://example.com/edu",
                    "source": "GOV_WEBSITE",
                },
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
    g = politician_citation_gaps(p)
    assert g is not None
    assert g.get("education_indices") == [0]


def test_politician_needs_iff_gaps_nonempty() -> None:
    cite = {"link": "https://example.com/", "source": "NEWS"}
    complete = {
        "education": [{"q": "B", "citation": cite}],
        "political_background": {"elections": [], "summary": None},
        "social_media": {"twitter": "https://twitter.com/a"},
        "social_media_citations": {"twitter": cite},
        "family_background": [],
        "criminal_records": [],
        "contact": {},
    }
    assert politician_needs_citation_audit(complete) is False
    assert politician_citation_gaps(complete) is None


def test_politician_citation_gaps_election_already_cited_others_remain() -> None:
    cite = {"link": "https://eci.example/", "source": "ECI"}
    pol = {
        "type": "MP",
        "political_background": {
            "elections": [
                {
                    "year": 2024,
                    "type": "MP",
                    "citation": cite,
                }
            ]
        },
        "education": [
            {"qualification": "MASTER", "institution": "null"},
            {"qualification": "PROFESSIONAL", "institution": "null"},
        ],
        "social_media": {
            "twitter": "https://twitter.com/z",
            "facebook": "",
            "instagram": None,
            "linkedin": None,
            "youtube": "",
            "website": "",
        },
        "contact": {"email": None, "phone": None, "address": "Street 1"},
        "family_background": [{"name": "A", "relation": "FATHER"}],
        "criminal_records": [{"name": "case", "type": "OTHERS"}],
        "performance": {"attendance": 77, "questions": None, "debates": None},
    }
    gaps = politician_citation_gaps(pol)
    assert gaps is not None
    assert "elections_indices" not in gaps
    assert gaps["education_indices"] == [0, 1]
    assert gaps["family_indices"] == [0]
    assert gaps["criminal_indices"] == [0]
    assert gaps["social_media_keys"] == ["twitter"]
    assert gaps["contact_keys"] == ["address"]
    assert gaps["performance_keys"] == ["attendance"]


def test_citation_audit_prompt_includes_targeted_backlog_when_provided() -> None:
    pol = {
        "education": [{}],
        "political_background": {"elections": [], "summary": None},
        "social_media": {},
        "family_background": [],
        "criminal_records": [],
        "contact": {},
    }
    g = politician_citation_gaps(pol)
    txt = PoliticianPrompts.citation_audit(pol, citation_backlog=g)
    assert "CITATION_BACKLOG_JSON" in txt
    assert "education_indices" in txt
    txt_no_bg = PoliticianPrompts.citation_audit(pol, citation_backlog=None)
    assert "CITATION_BACKLOG_JSON" not in txt_no_bg


def test_politician_citation_coverage_pct_no_slots_returns_none() -> None:
    assert politician_citation_coverage_pct({}) is None
    assert politician_citation_coverage_summary({}) == {
        "cited_fields_count": 0,
        "checkable_fields_count": 0,
        "sourced_pct": None,
    }
    assert (
        politician_citation_coverage_pct(
            {
                "education": [],
                "political_background": {"elections": [], "summary": None},
            }
        )
        is None
    )


def _edu_fixture(n_cited: int, n_slots: int) -> dict:
    cite = {"link": "https://example.com/x", "source": "NEWS"}
    rows = [{"citation": cite} if i < n_cited else {} for i in range(n_slots)]
    return {
        "education": rows,
        "political_background": {"elections": [], "summary": None},
    }


def test_politician_citation_coverage_pct_below_threshold_is_strictly_below_40() -> (
    None
):
    pct = politician_citation_coverage_pct(_edu_fixture(9, 25))
    assert pct is not None
    assert pct < CITATION_COVERAGE_SKIP_THRESHOLD_PCT


def test_politician_citation_coverage_pct_at_threshold_is_exactly_40() -> None:
    pct = politician_citation_coverage_pct(_edu_fixture(10, 25))
    assert pct == pytest.approx(CITATION_COVERAGE_SKIP_THRESHOLD_PCT)


def test_politician_citation_coverage_pct_contact_slots() -> None:
    pct = politician_citation_coverage_pct(
        {
            "education": [],
            "political_background": {"elections": [], "summary": None},
            "contact": {"email": "a@b.c"},
            "contact_citations": {},
        }
    )
    assert pct == pytest.approx(0.0)


def test_politician_citation_coverage_pct_performance_mp_slots() -> None:
    pct = politician_citation_coverage_pct(
        {
            "type": "MP",
            "education": [],
            "political_background": {"elections": [], "summary": None},
            "performance": {"attendance": 80, "questions": None, "debates": None},
            "performance_citations": {},
        }
    )
    assert pct == pytest.approx(0.0)


def test_politician_citation_coverage_summary_returns_fraction_and_counts() -> None:
    summary = politician_citation_coverage_summary(
        {
            "type": "MP",
            "education": [
                {
                    "qualification": "BACHELOR",
                    "citation": {"link": "https://x.y", "source": "NEWS"},
                },
                {"qualification": "MASTER"},
            ],
            "political_background": {
                "elections": [
                    {
                        "year": 2024,
                        "type": "MP",
                        "state": "Bihar",
                        "constituency": "Patna",
                        "party": "X",
                        "status": "WON",
                    }
                ],
                "summary": "Summary",
                "summary_citation": {"link": "https://x.z", "source": "NEWS"},
            },
            "contact": {"email": "a@b.c"},
            "contact_citations": {
                "email": {
                    "link": "https://contact.example",
                    "source": "GOV_WEBSITE",
                }
            },
            "performance": {"attendance": 80, "questions": None, "debates": 0},
            "performance_citations": {
                "attendance": {"link": "https://perf.example", "source": "ECI"}
            },
        }
    )
    assert summary == {
        "cited_fields_count": 4,
        "checkable_fields_count": 7,
        "sourced_pct": pytest.approx(4 / 7, abs=1e-6),
    }


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


def test_citation_audit_llm_accepts_null_social_dict_entries() -> None:
    """Gemini often emits null for unused social keys; schema must accept it."""
    audit = CitationAuditLLMResult.model_validate(
        {
            "social_media_citations": {
                "twitter": {"link": "https://x.com/a", "source": "NEWS"},
                "linkedin": None,
            }
        }
    )
    assert audit.social_media_citations is not None
    assert audit.social_media_citations["twitter"] is not None
    assert audit.social_media_citations["linkedin"] is None


def test_is_llm_quota_exc_matches_freetier_message() -> None:
    assert _is_llm_quota_exc(
        RuntimeError("FreeTierLLM: all candidates skipped or failed")
    )
    assert _is_llm_quota_exc(
        RuntimeError("RAJNITI_LLM_MAX_CALLS (5) exhausted for this run")
    )
    assert not _is_llm_quota_exc(ValueError("something else"))
