"""Unit tests for PoliticianService catalog and sitemap methods."""

import json
from pathlib import Path

import pytest

from app.services.politician_service import PoliticianService


@pytest.fixture
def catalog_service(tmp_path: Path) -> PoliticianService:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    mp_records = []
    for i in range(5):
        party = "Bharatiya Janata Party" if i < 2 else "Indian National Congress"
        mp_records.append(
            {
                "id": f"00000000-0000-0000-0000-00000000000{i}",
                "name": f"MP {i}",
                "state": "Gujarat" if i < 3 else "Maharashtra",
                "constituency": f"Constituency {i}",
                "type": "MP",
                "political_background": {"elections": [{"party": party}]},
            }
        )
    (data_dir / "mp.json").write_text(json.dumps(mp_records), encoding="utf-8")
    (data_dir / "mla.json").write_text("[]", encoding="utf-8")
    return PoliticianService(data_dir=data_dir)


@pytest.mark.unit
class TestPoliticianServiceCatalog:
    def test_list_catalog_pagination(self, catalog_service: PoliticianService) -> None:
        page1 = catalog_service.list_catalog(page=1, per_page=2)
        assert page1["total"] == 5
        assert page1["page"] == 1
        assert page1["per_page"] == 2
        assert len(page1["politicians"]) == 2

        page2 = catalog_service.list_catalog(page=2, per_page=2)
        assert len(page2["politicians"]) == 2

        page3 = catalog_service.list_catalog(page=3, per_page=2)
        assert len(page3["politicians"]) == 1

    def test_list_catalog_state_filter(self, catalog_service: PoliticianService) -> None:
        result = catalog_service.list_catalog(state="Gujarat")
        assert result["total"] == 3
        assert all(p["state"] == "Gujarat" for p in result["politicians"])

    def test_list_catalog_name_search(self, catalog_service: PoliticianService) -> None:
        result = catalog_service.list_catalog(q="mp 1")
        assert result["total"] == 1
        assert result["politicians"][0]["name"] == "MP 1"

    def test_list_catalog_party_filter(self, catalog_service: PoliticianService) -> None:
        result = catalog_service.list_catalog(parties=["Bharatiya Janata Party"])
        assert result["total"] == 2
        assert all(p["party"] == "Bharatiya Janata Party" for p in result["politicians"])

        multi = catalog_service.list_catalog(
            parties=["Bharatiya Janata Party", "Indian National Congress"]
        )
        assert multi["total"] == 5

    def test_list_catalog_returns_lightweight_fields(
        self, catalog_service: PoliticianService
    ) -> None:
        result = catalog_service.list_catalog(page=1, per_page=1)
        record = result["politicians"][0]
        assert set(record.keys()) == {
            "id",
            "slug",
            "name",
            "type",
            "state",
            "constituency",
            "photo",
            "party",
        }

    def test_sitemap_entries_includes_slugs(
        self, catalog_service: PoliticianService
    ) -> None:
        entries = catalog_service.sitemap_entries()
        assert len(entries) == 5
        assert all("slug" in e and e["slug"] for e in entries)
