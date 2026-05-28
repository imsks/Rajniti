"""Tests for StateMLAFetcher orchestrator (app.agents.state_mla_fetcher)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from app.agents.mla_fetcher import LARGE_STATES, LETTER_BUCKETS, fetch_all_constituencies


@pytest.mark.unit
def test_uttar_pradesh_uses_letter_buckets_not_single_shot() -> None:
    """UP has ~403 ACs; one JSON array is unreliable — expect one LLM call per bucket."""
    agent = MagicMock()
    agent._run_llm.return_value = '["Placeholder"]'
    agent._llm_call_count = 0
    agent.llm = MagicMock()

    def _parse(t: str):
        try:
            return json.loads(t.strip())
        except Exception:
            return None

    agent._parse_json_value.side_effect = _parse
    agent._coerce_to_list.side_effect = lambda x: x if isinstance(x, list) else None

    out = fetch_all_constituencies(agent, "Uttar Pradesh")

    assert agent._run_llm.call_count == len(LETTER_BUCKETS)
    assert len(out) == 1  # same placeholder deduped across buckets


@pytest.mark.unit
def test_small_state_single_llm_call() -> None:
    agent = MagicMock()
    agent._run_llm.return_value = '["Panaji", "Margao"]'
    agent._llm_call_count = 0
    agent.llm = MagicMock()

    def _parse(t: str):
        return json.loads(t.strip())

    agent._parse_json_value.side_effect = _parse
    agent._coerce_to_list.side_effect = lambda x: x if isinstance(x, list) else None

    out = fetch_all_constituencies(agent, "Goa")

    assert agent._run_llm.call_count == 1
    assert out == ["Panaji", "Margao"]


@pytest.mark.unit
def test_uttar_pradesh_listed_for_bucketed_fetch() -> None:
    assert "Uttar Pradesh" in LARGE_STATES
