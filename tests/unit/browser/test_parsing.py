"""Tests for browser/parsing helpers."""

import pytest

from app.browser.parsing import parse_agent_json_object


def test_parse_agent_json_object_strips_markdown() -> None:
    text = '```json\n{"financial_disclosure": {"total_assets_inr": 100}}\n```'
    data = parse_agent_json_object(text)
    assert data["financial_disclosure"]["total_assets_inr"] == 100


def test_parse_agent_json_object_empty_raises() -> None:
    with pytest.raises(ValueError, match="Empty"):
        parse_agent_json_object("")


def test_parse_agent_json_object_invalid_raises() -> None:
    with pytest.raises(Exception):
        parse_agent_json_object("not json")
