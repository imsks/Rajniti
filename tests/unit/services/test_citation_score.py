"""Unit tests for PoliticianService.compute_citation_score."""

import pytest

from app.services.politician_service import PoliticianService


def _politician(**kwargs):
    """Minimal politician dict with sensible defaults."""
    base = {
        "id": "test-id",
        "name": "Test Politician",
        "state": "Maharashtra",
        "constituency": "Mumbai North",
        "type": "MP",
        "political_background": {"elections": []},
    }
    base.update(kwargs)
    return base


@pytest.mark.unit
class TestComputeCitationScore:
    def test_empty_politician_returns_zero(self) -> None:
        p = _politician()
        assert PoliticianService.compute_citation_score(p) == 0.0

    def test_all_elections_cited(self) -> None:
        p = _politician(
            political_background={
                "elections": [
                    {"year": 2024, "party": "BJP", "citation": {"link": "http://a.com", "source": "ECI"}},
                    {"year": 2019, "party": "BJP", "citation": {"link": "http://b.com", "source": "ECI"}},
                ]
            }
        )
        assert PoliticianService.compute_citation_score(p) == 1.0

    def test_partial_elections_cited(self) -> None:
        p = _politician(
            political_background={
                "elections": [
                    {"year": 2024, "party": "BJP", "citation": {"link": "http://a.com", "source": "ECI"}},
                    {"year": 2019, "party": "BJP"},
                ]
            }
        )
        assert PoliticianService.compute_citation_score(p) == 0.5

    def test_summary_with_citation(self) -> None:
        p = _politician(
            political_background={
                "elections": [],
                "summary": "A great politician",
                "summary_citation": {"link": "http://a.com", "source": "NEWS"},
            }
        )
        assert PoliticianService.compute_citation_score(p) == 1.0

    def test_summary_without_citation(self) -> None:
        p = _politician(
            political_background={
                "elections": [],
                "summary": "A great politician",
            }
        )
        assert PoliticianService.compute_citation_score(p) == 0.0

    def test_contact_fields_cited(self) -> None:
        p = _politician(
            contact={"email": "test@test.com", "phone": None, "address": "123 St"},
            contact_citations={"email": {"link": "http://a.com", "source": "GOV_WEBSITE"}},
        )
        score = PoliticianService.compute_citation_score(p)
        # 2 non-null contact fields, 1 cited → 0.5
        assert score == 0.5

    def test_social_media_cited(self) -> None:
        p = _politician(
            social_media={"twitter": "https://twitter.com/x", "facebook": None},
            social_media_citations={"twitter": {"link": "http://a.com", "source": "OTHERS"}},
        )
        score = PoliticianService.compute_citation_score(p)
        # 1 non-null social field, 1 cited → 1.0
        assert score == 1.0

    def test_performance_zero_values_excluded(self) -> None:
        """Zero performance values should not inflate the denominator."""
        p = _politician(
            performance={"attendance": 0, "questions": 0, "debates": 0},
        )
        assert PoliticianService.compute_citation_score(p) == 0.0

    def test_performance_nonzero_cited(self) -> None:
        p = _politician(
            performance={"attendance": 80, "questions": 20, "debates": 5},
            performance_citations={"attendance": {"link": "http://a.com", "source": "GOV_WEBSITE"}},
        )
        score = PoliticianService.compute_citation_score(p)
        # 3 non-zero performance fields, 1 cited → 1/3
        assert abs(score - 1 / 3) < 1e-9

    def test_mixed_fields_correct_ratio(self) -> None:
        p = _politician(
            political_background={
                "elections": [
                    {"year": 2024, "party": "BJP", "citation": {"link": "http://a.com", "source": "ECI"}},
                ]
            },
            education=[
                {"qualification": "BA", "citation": None},
            ],
        )
        score = PoliticianService.compute_citation_score(p)
        # total=2, cited=1 → 0.5
        assert score == 0.5

    def test_score_is_float_in_range(self) -> None:
        import json
        from pathlib import Path

        data_path = Path(__file__).resolve().parents[3] / "app" / "data" / "mp.json"
        with open(data_path, encoding="utf-8") as f:
            politicians = json.load(f)

        for p in politicians[:20]:
            score = PoliticianService.compute_citation_score(p)
            assert 0.0 <= score <= 1.0
