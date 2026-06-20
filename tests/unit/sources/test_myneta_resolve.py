"""MyNeta URL resolve helper tests."""

import pytest

from app.sources.myneta_resolve import (
    build_resolve_instructions,
    build_search_url,
    parse_resolve_result,
)


def test_build_search_url() -> None:
    assert build_search_url("Bihar2025") == "https://www.myneta.info/Bihar2025/"


def test_build_resolve_instructions_includes_candidate_fields() -> None:
    text = build_resolve_instructions("Alice", "Bihar", "AC-1", "Bihar2025")
    assert "Alice" in text
    assert "AC-1" in text
    assert "candidate.php" in text


def test_parse_resolve_result_from_json() -> None:
    raw = (
        '{"url":"https://www.myneta.info/Bihar2025/candidate.php?candidate_id=9",'
        '"candidate_id":"9","election_slug":"Bihar2025"}'
    )
    parsed = parse_resolve_result(raw, "Bihar2025")
    assert parsed.url == "https://www.myneta.info/Bihar2025/candidate.php?candidate_id=9"
    assert parsed.candidate_id == "9"
    assert parsed.election_slug == "Bihar2025"


def test_parse_resolve_result_regex_fallback() -> None:
    raw = "Found profile at https://www.myneta.info/Bihar2025/candidate.php?candidate_id=42"
    parsed = parse_resolve_result(raw, "Bihar2025")
    assert parsed.candidate_id == "42"
    assert "candidate_id=42" in (parsed.url or "")


def test_parse_resolve_result_empty() -> None:
    parsed = parse_resolve_result("", "Bihar2025")
    assert parsed.url is None
    assert parsed.raw_result == ""
