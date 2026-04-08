"""Tests for PoliticianService.update_politician (agent persistence)."""

import json
from pathlib import Path

import pytest

from app.services.politician_service import PoliticianService


@pytest.mark.unit
class TestUpdatePolitician:
    def test_updates_mp_json_and_returns_true(self, tmp_path: Path) -> None:
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        pid = "11111111-1111-1111-1111-111111111111"
        original = [
            {
                "id": pid,
                "name": "Test MP",
                "state": "Test",
                "education": [],
            }
        ]
        mp_path = data_dir / "mp.json"
        mp_path.write_text(json.dumps(original), encoding="utf-8")

        svc = PoliticianService(data_dir=data_dir)
        ok = svc.update_politician(
            pid, {"education": [{"institution": "X", "degree": "Y", "year": 2020}]}
        )

        assert ok is True
        loaded = json.loads(mp_path.read_text(encoding="utf-8"))
        assert loaded[0]["education"][0]["institution"] == "X"

    def test_finds_mla_file(self, tmp_path: Path) -> None:
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        pid = "22222222-2222-2222-2222-222222222222"
        mla_path = data_dir / "mla.json"
        mla_path.write_text(
            json.dumps([{"id": pid, "name": "MLA", "education": []}]),
            encoding="utf-8",
        )

        svc = PoliticianService(data_dir=data_dir)
        assert svc.update_politician(pid, {"name": "Updated"}) is True
        loaded = json.loads(mla_path.read_text(encoding="utf-8"))
        assert loaded[0]["name"] == "Updated"

    def test_unknown_id_returns_false(self, tmp_path: Path) -> None:
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "mp.json").write_text("[]", encoding="utf-8")

        svc = PoliticianService(data_dir=data_dir)
        assert (
            svc.update_politician("00000000-0000-0000-0000-000000000000", {"x": 1})
            is False
        )

    def test_empty_updates_returns_false(self, tmp_path: Path) -> None:
        svc = PoliticianService(data_dir=tmp_path)
        assert svc.update_politician("x", {}) is False

    def test_syncs_by_id_index_when_slugs_built(self, tmp_path: Path) -> None:
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        pid = "33333333-3333-3333-3333-333333333333"
        (data_dir / "mp.json").write_text(
            json.dumps([{"id": pid, "name": "A", "education": []}]),
            encoding="utf-8",
        )

        svc = PoliticianService(data_dir=data_dir)
        svc._ensure_slugs()
        assert svc.get_by_id(pid) is not None

        assert svc.update_politician(pid, {"education": [{"degree": "B.A."}]}) is True
        assert svc.get_by_id(pid)["education"][0]["degree"] == "B.A."
