"""CLI defaults for scripts/scrape_election.py."""

import pytest

from app.scrapers.defaults import resolve_scrape_target


def test_resolve_defaults_to_mla_bihar_2025() -> None:
    url, etype = resolve_scrape_target(None, None)
    assert etype == "MLA"
    assert "ResultAcGenNov2025" in url


def test_resolve_type_mla_uses_default_url() -> None:
    url, etype = resolve_scrape_target(None, "MLA")
    assert etype == "MLA"
    assert "ResultAcGenNov2025" in url


def test_resolve_type_mp_uses_default_url() -> None:
    url, etype = resolve_scrape_target(None, "MP")
    assert etype == "MP"
    assert "PcResultGenJune2024" in url


def test_resolve_url_auto_detects_mla() -> None:
    url, etype = resolve_scrape_target(
        "https://results.eci.gov.in/ResultAcGenNov2025", None
    )
    assert etype == "MLA"
    assert url.endswith("ResultAcGenNov2025")


def test_resolve_unknown_url_without_type_raises() -> None:
    with pytest.raises(ValueError, match="auto-detect"):
        resolve_scrape_target("https://example.com/election", None)
