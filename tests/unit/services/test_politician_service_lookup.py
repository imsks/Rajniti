"""Tests for PoliticianService slug and id lookup."""

import json
from pathlib import Path

import pytest

from app.services.politician_service import PoliticianService


def _write_mp(data_dir: Path, records: list) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "mp.json").write_text(json.dumps(records), encoding="utf-8")
    (data_dir / "mla.json").write_text("[]", encoding="utf-8")


@pytest.fixture
def svc(tmp_path: Path) -> PoliticianService:
    pid = "8fba2f3f-b5a9-4440-a1c9-caf514cb3b8c"
    _write_mp(
        tmp_path,
        [
            {
                "id": pid,
                "name": "Narendra Modi",
                "state": "Gujarat",
                "constituency": "Varanasi",
                "type": "MP",
                "political_background": {
                    "elections": [
                        {
                            "year": 2024,
                            "type": "LS",
                            "state": "UP",
                            "constituency": "Varanasi",
                            "party": "BJP",
                            "status": "WON",
                        }
                    ]
                },
            }
        ],
    )
    return PoliticianService(data_dir=tmp_path)


@pytest.mark.unit
class TestPoliticianServiceLookup:
    def test_get_by_slug_exact(self, svc: PoliticianService) -> None:
        p = svc.get_by_slug("narendra-modi")
        assert p is not None
        assert p["name"] == "Narendra Modi"

    def test_get_by_slug_with_short_id_suffix(self, svc: PoliticianService) -> None:
        p = svc.get_by_slug("narendra-modi-8fba2f3f")
        assert p is not None
        assert p["id"] == "8fba2f3f-b5a9-4440-a1c9-caf514cb3b8c"

    def test_get_by_slug_unknown_returns_none(self, svc: PoliticianService) -> None:
        assert svc.get_by_slug("nonexistent-person") is None

    def test_get_by_id_case_insensitive(self, svc: PoliticianService) -> None:
        upper = "8FBA2F3F-B5A9-4440-A1C9-CAF514CB3B8C"
        p = svc.get_by_id(upper)
        assert p is not None
        assert p["name"] == "Narendra Modi"

    def test_disambiguated_slug_for_duplicate_names(self, tmp_path: Path) -> None:
        _write_mp(
            tmp_path,
            [
                {
                    "id": "aaaa1111-1111-1111-1111-111111111111",
                    "name": "John Smith",
                    "state": "A",
                    "constituency": "X",
                    "type": "MP",
                    "political_background": {"elections": []},
                },
                {
                    "id": "bbbb2222-2222-2222-2222-222222222222",
                    "name": "John Smith",
                    "state": "B",
                    "constituency": "Y",
                    "type": "MP",
                    "political_background": {"elections": []},
                },
            ],
        )
        svc = PoliticianService(data_dir=tmp_path)
        a = svc.get_by_slug("john-smith-aaaa1111")
        b = svc.get_by_slug("john-smith-bbbb2222")
        assert a is not None and b is not None
        assert a["id"] != b["id"]
