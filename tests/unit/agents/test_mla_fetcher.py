"""Tests for the simple queue-based MLA fetcher (app.agents.mla_fetcher)."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.agents.mla_fetcher import (
    FetchQueue,
    FetchResult,
    dedupe_key,
    fetch_all_constituencies,
    get_existing_constituencies,
    load_existing_mlas,
    load_states,
    make_id,
    persist_record,
    run_fetcher,
    state_has_data,
    validate_state,
)


# ---------------------------------------------------------------------------
# Pure Python helper tests
# ---------------------------------------------------------------------------


class TestValidateState:
    def test_found(self):
        states = ["Goa", "Bihar", "Uttar Pradesh"]
        assert validate_state("goa", states) == "Goa"
        assert validate_state("Uttar Pradesh", states) == "Uttar Pradesh"
        assert validate_state("  Bihar  ", states) == "Bihar"

    def test_not_found(self):
        states = ["Goa", "Bihar"]
        assert validate_state("InvalidState", states) is None

    def test_empty(self):
        assert validate_state("", []) is None


class TestLoadStates:
    def test_loads_from_file(self, tmp_path):
        states_file = tmp_path / "states.json"
        states_file.write_text('["Goa", "Bihar"]')
        result = load_states(tmp_path)
        assert result == ["Goa", "Bihar"]

    def test_missing_file(self, tmp_path):
        result = load_states(tmp_path)
        assert result == []


class TestLoadExistingMlas:
    def test_loads_for_state(self, tmp_path):
        mla_file = tmp_path / "mla.json"
        records = [
            {"name": "A", "state": "Goa", "constituency": "Panaji"},
            {"name": "B", "state": "Bihar", "constituency": "Patna"},
        ]
        mla_file.write_text(json.dumps(records))
        result = load_existing_mlas(mla_file, "Goa")
        assert len(result) == 1
        assert result[0]["name"] == "A"

    def test_missing_file(self, tmp_path):
        result = load_existing_mlas(tmp_path / "mla.json", "Goa")
        assert result == []


class TestStateHasData:
    def test_true(self, tmp_path):
        mla_file = tmp_path / "mla.json"
        mla_file.write_text(json.dumps([{"name": "X", "state": "Goa", "constituency": "Y"}]))
        assert state_has_data(mla_file, "Goa") is True

    def test_false_no_records(self, tmp_path):
        mla_file = tmp_path / "mla.json"
        mla_file.write_text(json.dumps([{"name": "X", "state": "Bihar", "constituency": "Y"}]))
        assert state_has_data(mla_file, "Goa") is False

    def test_false_no_file(self, tmp_path):
        assert state_has_data(tmp_path / "mla.json", "Goa") is False


class TestGetExistingConstituencies:
    def test_extracts_lowercase(self):
        records = [
            {"constituency": "Panaji"},
            {"constituency": "Margao"},
            {"constituency": "Panaji"},  # duplicate
        ]
        result = get_existing_constituencies(records)
        assert result == {"panaji", "margao"}


class TestHelpers:
    def test_dedupe_key(self):
        assert dedupe_key("John Doe", "Panaji") == "john doe|panaji"

    def test_make_id_deterministic(self):
        id1 = make_id("John", "Goa", "Panaji")
        id2 = make_id("John", "Goa", "Panaji")
        assert id1 == id2

    def test_make_id_case_insensitive(self):
        id1 = make_id("JOHN", "GOA", "PANAJI")
        id2 = make_id("john", "goa", "panaji")
        assert id1 == id2


# ---------------------------------------------------------------------------
# FetchQueue tests
# ---------------------------------------------------------------------------


class TestFetchQueue:
    def test_basic_flow(self):
        q = FetchQueue(state="Goa", pending=deque(["Panaji", "Margao", "Ponda"]))
        assert q.total == 3
        assert q.remaining == 3

        item = q.next()
        assert item == "Panaji"
        q.mark_done(item)
        assert q.remaining == 2
        assert len(q.completed) == 1

    def test_empty_returns_none(self):
        q = FetchQueue(state="Goa", pending=deque())
        assert q.next() is None


# ---------------------------------------------------------------------------
# Persist tests
# ---------------------------------------------------------------------------


class TestPersistRecord:
    def test_adds_new_record(self, tmp_path):
        mla_file = tmp_path / "mla.json"
        mla_file.write_text("[]")

        item = {"name": "John", "constituency": "Panaji", "party": "BJP"}
        result = persist_record(mla_file, "Goa", item)
        assert result is True

        data = json.loads(mla_file.read_text())
        assert len(data) == 1
        assert data[0]["name"] == "John"
        assert data[0]["state"] == "Goa"

    def test_skips_duplicate(self, tmp_path):
        mla_file = tmp_path / "mla.json"
        existing = [{"name": "John", "constituency": "Panaji", "state": "Goa"}]
        mla_file.write_text(json.dumps(existing))

        item = {"name": "John", "constituency": "Panaji", "party": "BJP"}
        result = persist_record(mla_file, "Goa", item)
        assert result is False

    def test_skips_empty_name(self, tmp_path):
        mla_file = tmp_path / "mla.json"
        mla_file.write_text("[]")

        item = {"name": "", "constituency": "Panaji", "party": "BJP"}
        result = persist_record(mla_file, "Goa", item)
        assert result is False

    def test_creates_file_if_missing(self, tmp_path):
        mla_file = tmp_path / "mla.json"
        item = {"name": "Test", "constituency": "ABC", "party": "INC"}
        result = persist_record(mla_file, "Goa", item)
        assert result is True
        assert mla_file.exists()


# ---------------------------------------------------------------------------
# LLM fetch tests (mocked)
# ---------------------------------------------------------------------------


class TestFetchConstituencies:
    def test_small_state_single_shot(self):
        agent = MagicMock()
        agent._run_llm.return_value = '["Panaji", "Margao", "Ponda"]'
        agent._llm_call_count = 0
        agent._parse_json_value.side_effect = lambda t: json.loads(t.strip())
        agent._coerce_to_list.side_effect = lambda x: x if isinstance(x, list) else None
        agent.llm = MagicMock()

        result = fetch_all_constituencies(agent, "Goa")
        assert result == ["Panaji", "Margao", "Ponda"]
        assert agent._run_llm.call_count == 1

    def test_large_state_uses_buckets(self):
        agent = MagicMock()
        agent._run_llm.return_value = '["Test"]'
        agent._llm_call_count = 0
        agent._parse_json_value.side_effect = lambda t: json.loads(t.strip())
        agent._coerce_to_list.side_effect = lambda x: x if isinstance(x, list) else None
        agent.llm = MagicMock()

        result = fetch_all_constituencies(agent, "Uttar Pradesh")
        # Should call LLM once per bucket (6 buckets)
        assert agent._run_llm.call_count == 6
        # Deduplicates across buckets
        assert result == ["Test"]


# ---------------------------------------------------------------------------
# Full run_fetcher tests
# ---------------------------------------------------------------------------


class TestRunFetcher:
    def _setup_data_dir(self, tmp_path, states=None, mla_records=None):
        """Helper to create data dir with states.json and mla.json."""
        if states is None:
            states = ["Goa", "Bihar"]
        (tmp_path / "states.json").write_text(json.dumps(states))
        if mla_records is None:
            mla_records = []
        (tmp_path / "mla.json").write_text(json.dumps(mla_records))
        return tmp_path

    def test_invalid_state_fails(self, tmp_path):
        data_dir = self._setup_data_dir(tmp_path)
        agent = MagicMock()

        result = run_fetcher(agent, "InvalidState", data_dir)
        assert result.ok is False
        assert "not found" in result.error

    def test_dry_run_no_llm_calls(self, tmp_path):
        existing = [{"name": "X", "state": "Goa", "constituency": "Panaji"}]
        data_dir = self._setup_data_dir(tmp_path, mla_records=existing)
        agent = MagicMock()

        result = run_fetcher(agent, "Goa", data_dir, dry_run=True)
        assert result.ok is True
        assert agent._run_llm.call_count == 0

    @patch("app.agents.mla_fetcher.fetch_all_constituencies")
    def test_skips_when_all_exist(self, mock_fetch_c, tmp_path):
        existing = [
            {"name": "A", "state": "Goa", "constituency": "Panaji"},
            {"name": "B", "state": "Goa", "constituency": "Margao"},
        ]
        data_dir = self._setup_data_dir(tmp_path, mla_records=existing)
        mock_fetch_c.return_value = ["Panaji", "Margao"]

        agent = MagicMock()
        result = run_fetcher(agent, "Goa", data_dir)
        assert result.ok is True
        assert result.added == 0
        assert result.constituencies_found == 2

    @patch("app.agents.mla_fetcher.fetch_mla_for_constituency")
    @patch("app.agents.mla_fetcher.fetch_all_constituencies")
    def test_fetches_missing_constituency(self, mock_fetch_c, mock_fetch_mla, tmp_path):
        existing = [{"name": "A", "state": "Goa", "constituency": "Panaji"}]
        data_dir = self._setup_data_dir(tmp_path, mla_records=existing)
        mock_fetch_c.return_value = ["Panaji", "Margao"]
        mock_fetch_mla.return_value = {"name": "B", "constituency": "Margao", "party": "INC"}

        agent = MagicMock()
        result = run_fetcher(agent, "Goa", data_dir)
        assert result.ok is True
        assert result.added == 1
        assert result.fetched == 1

        # Verify it was persisted
        data = json.loads((data_dir / "mla.json").read_text())
        names = [r["name"] for r in data]
        assert "B" in names

    @patch("app.agents.mla_fetcher.fetch_all_constituencies")
    def test_no_constituencies_is_error(self, mock_fetch_c, tmp_path):
        data_dir = self._setup_data_dir(tmp_path)
        mock_fetch_c.return_value = []

        agent = MagicMock()
        result = run_fetcher(agent, "Goa", data_dir)
        assert result.ok is False
        assert "Failed to fetch" in result.error
