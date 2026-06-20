"""Politician enrich route tests."""

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
        "political_background": {"elections": []},
    }
    (data_dir / "mla.json").write_text(json.dumps([politician]), encoding="utf-8")
    (data_dir / "mp.json").write_text("[]", encoding="utf-8")
    return PoliticianService(data_dir=data_dir)


@pytest.fixture
def enrich_client(app, politician_service: PoliticianService):
    with patch(
        "app.routes.scrape_routes._politician_service",
        politician_service,
    ):
        with app.test_client() as c:
            yield c, politician_service


@pytest.mark.unit
def test_enrich_success(enrich_client) -> None:
    client, _service = enrich_client
    pid = "ef8a4654-1d09-4a06-bae7-14377bc08387"
    mock_result = {
        "ok": True,
        "id": pid,
        "updated_fields": ["education"],
        "process_results": [
            {"process": "source_sync", "ok": True, "sources_run": ["myneta"]},
            {"process": "citation_backfill", "ok": True},
        ],
    }
    with patch("app.agents.politician_agent.PoliticianAgent") as mock_agent_cls:
        mock_agent = mock_agent_cls.return_value
        mock_agent.run.return_value = mock_result
        resp = client.post(
            f"/api/v1/politicians/{pid}/enrich",
            json={"sources": ["myneta"], "force": True},
        )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["enrichment"]["process_results"][0]["process"] == "source_sync"
    mock_agent.run.assert_called_once()


@pytest.mark.unit
def test_enrich_politician_not_found(client) -> None:
    resp = client.post(
        "/api/v1/politicians/missing-id/enrich",
        json={"sources": ["myneta"]},
    )
    assert resp.status_code == 404
