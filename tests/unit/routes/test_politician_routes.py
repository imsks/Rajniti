"""Unit tests for politician API routes (no legacy data_service mock)."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.politician_service import PoliticianService


@pytest.fixture
def politician_service(tmp_path: Path) -> PoliticianService:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    pid = "ef8a4654-1d09-4a06-bae7-14377bc08387"
    (data_dir / "mp.json").write_text(
        json.dumps(
            [
                {
                    "id": pid,
                    "name": "NARENDRA MODI",
                    "state": "Gujarat",
                    "constituency": "Varanasi",
                    "type": "MP",
                    "political_background": {"elections": []},
                }
            ]
        ),
        encoding="utf-8",
    )
    (data_dir / "mla.json").write_text("[]", encoding="utf-8")
    return PoliticianService(data_dir=data_dir)


@pytest.fixture
def client(app, politician_service: PoliticianService):
    with patch(
        "app.routes.api_routes.politician_ctrl.service",
        politician_service,
    ):
        with app.test_client() as c:
            yield c


@pytest.mark.unit
class TestPoliticianRoutes:
    def test_get_politician_by_slug_200(self, client) -> None:
        response = client.get("/api/v1/politicians/slug/narendra-modi")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["name"] == "NARENDRA MODI"
        assert data["data"]["sourced_pct"] is None
        assert data["data"]["cited_fields_count"] == 0
        assert data["data"]["checkable_fields_count"] == 0

    def test_get_politician_by_slug_404(self, client) -> None:
        response = client.get("/api/v1/politicians/slug/does-not-exist")
        assert response.status_code == 404
        assert response.get_json()["success"] is False

    def test_get_politician_by_id_200(self, client) -> None:
        pid = "ef8a4654-1d09-4a06-bae7-14377bc08387"
        response = client.get(f"/api/v1/politicians/{pid}")
        assert response.status_code == 200
        assert response.get_json()["data"]["id"] == pid

    def test_get_politician_by_id_case_insensitive(self, client) -> None:
        pid = "EF8A4654-1D09-4A06-BAE7-14377BC08387"
        response = client.get(f"/api/v1/politicians/{pid}")
        assert response.status_code == 200

    def test_get_politician_by_id_404(self, client) -> None:
        response = client.get(
            "/api/v1/politicians/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404

    def test_catalog_pagination_200(self, client) -> None:
        response = client.get("/api/v1/politicians/catalog?page=1&per_page=10")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "politicians" in data["data"]
        assert data["data"]["page"] == 1

    def test_catalog_type_filter_mp(self, client) -> None:
        response = client.get("/api/v1/politicians/catalog?type=MP")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert all(p["type"] == "MP" for p in data["data"]["politicians"])

    def test_sitemap_entries_200(self, client) -> None:
        response = client.get("/api/v1/politicians/sitemap-entries")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]["entries"]) >= 1
        assert "slug" in data["data"]["entries"][0]
