"""Tests for StateMLAFetcher / ConstituencyFetcher large-state behaviour."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from app.agents import state_mla_fetcher as smf


@pytest.mark.unit
def test_uttar_pradesh_uses_letter_buckets_not_single_shot() -> None:
    """UP has ~403 ACs; one JSON array is unreliable — expect one LLM call per bucket."""
    agent = MagicMock()
    agent._run_llm.return_value = '["Placeholder"]'

    def _parse(t: str):
        try:
            return json.loads(t.strip())
        except Exception:
            return None

    agent._parse_json_value.side_effect = _parse
    agent._coerce_to_list.side_effect = lambda x: x if isinstance(x, list) else None

    cf = smf.ConstituencyFetcher(agent)
    out = cf.run("Uttar Pradesh")

    assert agent._run_llm.call_count == len(smf._CONSTITUENCY_LETTER_BUCKETS)
    assert len(out) == 1  # same placeholder deduped across buckets


@pytest.mark.unit
def test_small_state_single_llm_call() -> None:
    agent = MagicMock()
    agent._run_llm.return_value = '["Panaji", "Margao"]'

    def _parse(t: str):
        return json.loads(t.strip())

    agent._parse_json_value.side_effect = _parse
    agent._coerce_to_list.side_effect = lambda x: x if isinstance(x, list) else None

    cf = smf.ConstituencyFetcher(agent)
    out = cf.run("Goa")

    assert agent._run_llm.call_count == 1
    assert out == ["Panaji", "Margao"]


@pytest.mark.unit
def test_mla_details_shrinks_batch_when_many_constituencies() -> None:
    agent = MagicMock()
    agent._run_llm.return_value = "[]"
    agent._parse_json_value.return_value = []
    agent._coerce_to_list.return_value = []

    fetcher = smf.MLADetailsFetcher(agent, batch_size=30, max_workers=3)
    n = 250
    constituencies = [f"AC{i}" for i in range(n)]
    fetcher.run("Uttar Pradesh", constituencies)

    assert agent._run_llm.call_count >= 1
    first_prompt = agent._run_llm.call_args_list[0][0][0]
    # batch cap 12 when n > 200 → first prompt embeds at most 12 constituency names
    assert first_prompt.count("AC") <= 12


@pytest.mark.unit
def test_uttar_pradesh_listed_for_bucketed_fetch() -> None:
    assert "Uttar Pradesh" in smf.STATES_REQUIRING_BUCKETED_CONSTITUENCY_FETCH
