"""Tests for PoliticianService.list_incomplete (incomplete profiles API)."""

import json
from pathlib import Path

import pytest

from app.services.politician_service import PoliticianService


def _politician(pid: str, name: str, *, cited: bool) -> dict:
    citation = {"url": "https://example.com"} if cited else None
    return {
        "id": pid,
        "name": name,
        "state": "Gujarat",
        "constituency": "Varanasi",
        "type": "MP",
        "education": [{"institution": "X", "citation": citation}],
        "family_background": [{"name": "Y", "citation": citation}],
        "criminal_records": [{"name": "Z", "citation": citation}],
        "contact": {"email": "a@example.com"},
        "contact_citations": {"email": citation} if cited else {},
        "political_background": {
            "elections": [{"year": "2024", "party": "BJP", "citation": citation}]
        },
    }


def _service(tmp_path: Path, records: list) -> PoliticianService:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "mp.json").write_text(json.dumps(records), encoding="utf-8")
    (data_dir / "mla.json").write_text("[]", encoding="utf-8")
    return PoliticianService(data_dir=data_dir)


@pytest.mark.unit
class TestListIncomplete:
    def test_only_returns_profiles_below_threshold(self, tmp_path: Path) -> None:
        svc = _service(
            tmp_path,
            [
                _politician(
                    "11111111-1111-1111-1111-111111111111", "Thin", cited=False
                ),
                _politician("22222222-2222-2222-2222-222222222222", "Full", cited=True),
            ],
        )

        result = svc.list_incomplete(limit=10)

        assert result["total"] == 1
        assert result["threshold"] == 0.5
        assert result["politicians"][0]["name"] == "Thin"
        assert result["politicians"][0]["sourced_pct"] == 0.0
        assert result["politicians"][0]["party"] == "BJP"

    def test_sorted_least_complete_first(self, tmp_path: Path) -> None:
        partial = _politician(
            "33333333-3333-3333-3333-333333333333", "Partial", cited=False
        )
        partial["education"][0]["citation"] = {"url": "https://example.com"}
        svc = _service(
            tmp_path,
            [
                partial,
                _politician(
                    "11111111-1111-1111-1111-111111111111", "Thin", cited=False
                ),
            ],
        )

        names = [p["name"] for p in svc.list_incomplete(limit=10)["politicians"]]

        assert names == ["Thin", "Partial"]

    def test_limit_and_offset_paginate(self, tmp_path: Path) -> None:
        records = [
            _politician(
                f"{i}{i}{i}{i}{i}{i}{i}{i}-1111-1111-1111-111111111111",
                f"P{i}",
                cited=False,
            )
            for i in range(1, 6)
        ]
        svc = _service(tmp_path, records)

        first = svc.list_incomplete(limit=2)
        second = svc.list_incomplete(limit=2, offset=2)

        assert first["total"] == 5
        assert len(first["politicians"]) == 2
        assert len(second["politicians"]) == 2
        assert {p["id"] for p in first["politicians"]}.isdisjoint(
            {p["id"] for p in second["politicians"]}
        )

    def test_daily_rotation_offsets_window(self, tmp_path: Path) -> None:
        records = [
            _politician(
                f"{i}{i}{i}{i}{i}{i}{i}{i}-1111-1111-1111-111111111111",
                f"P{i}",
                cited=False,
            )
            for i in range(1, 6)
        ]
        svc = _service(tmp_path, records)

        rotated = svc.list_incomplete(limit=2, daily_rotation=True)

        assert rotated["total"] == 5
        assert rotated["offset"] % 2 == 0
        assert rotated["offset"] < 6

    def test_election_type_filter(self, tmp_path: Path) -> None:
        svc = _service(
            tmp_path,
            [_politician("11111111-1111-1111-1111-111111111111", "Thin", cited=False)],
        )

        assert svc.list_incomplete(election_type="MLA", limit=10)["total"] == 0
        assert svc.list_incomplete(election_type="MP", limit=10)["total"] == 1

    def test_empty_profile_sorts_first(self, tmp_path: Path) -> None:
        empty = {
            "id": "99999999-9999-9999-9999-999999999999",
            "name": "Empty",
            "state": "Gujarat",
            "constituency": "Varanasi",
            "type": "MP",
            "political_background": {"elections": []},
        }
        svc = _service(
            tmp_path,
            [
                _politician(
                    "11111111-1111-1111-1111-111111111111", "Thin", cited=False
                ),
                empty,
            ],
        )

        result = svc.list_incomplete(limit=10)

        assert [p["name"] for p in result["politicians"]] == ["Empty", "Thin"]
        assert result["politicians"][0]["sourced_pct"] is None
