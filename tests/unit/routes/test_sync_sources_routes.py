"""Politician source sync route tests."""

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
    politician = {
        "id": pid,
        "name": "Test MLA",
        "state": "Bihar",
        "constituency": "AC",
        "type": "MLA",
        "political_background": {"elections": [{"year": 2025}]},
    }
    (data_dir / "mla.json").write_text(json.dumps([politician]), encoding="utf-8")
    (data_dir / "mp.json").write_text("[]", encoding="utf-8")
    return PoliticianService(data_dir=data_dir)


@pytest.fixture
def sync_client(app, politician_service: PoliticianService):
    with patch(
        "app.routes.scrape_routes._politician_service",
        politician_service,
    ):
        with patch(
            "app.routes.scrape_routes._orchestrator.politician_service",
            politician_service,
        ):
            with app.test_client() as c:
                yield c, politician_service


@pytest.mark.unit
def test_sync_sources_success(sync_client) -> None:
    client, service = sync_client
    pid = "ef8a4654-1d09-4a06-bae7-14377bc08387"
    sync_result = {
        "id": pid,
        "ok": True,
        "sources_run": ["myneta"],
        "issues": [],
        "errors": [],
    }
    with patch(
        "app.routes.scrape_routes._orchestrator.sync_politician",
        return_value=sync_result,
    ):
        resp = client.post(
            f"/api/v1/politicians/{pid}/sync-sources",
            json={"sources": ["myneta"], "force": True},
        )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["sync"]["sources_run"] == ["myneta"]
    assert data["data"]["politician"]["id"] == pid


@pytest.mark.unit
def test_sync_sources_politician_not_found(client) -> None:
    resp = client.post(
        "/api/v1/politicians/missing-id/sync-sources",
        json={"sources": ["myneta"]},
    )
    assert resp.status_code == 404
    assert resp.get_json()["success"] is False
