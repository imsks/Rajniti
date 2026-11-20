"""Unit tests for incomplete-profile and service-token ingest routes."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.politician_service import PoliticianService

TOKEN = "test-service-token"


def _thin(pid: str, name: str) -> dict:
    return {
        "id": pid,
        "name": name,
        "state": "Gujarat",
        "constituency": "Varanasi",
        "type": "MP",
        "education": [{"institution": "X"}],
        "political_background": {"elections": [{"year": "2024", "party": "BJP"}]},
    }


@pytest.fixture
def politician_service(tmp_path: Path) -> PoliticianService:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    records = [
        _thin(f"{i}{i}{i}{i}{i}{i}{i}{i}-1111-1111-1111-111111111111", f"P{i}")
        for i in range(1, 9)
    ]
    (data_dir / "mp.json").write_text(json.dumps(records), encoding="utf-8")
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


@pytest.fixture
def service_token(monkeypatch):
    monkeypatch.setenv("RAJNITI_SERVICE_TOKEN", TOKEN)
    return TOKEN


@pytest.mark.unit
class TestIncompleteRoute:
    def test_public_caller_capped_at_five(self, client) -> None:
        response = client.get("/api/v1/politicians/incomplete")

        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["total"] == 8
        assert data["daily_max"] == 5
        assert len(data["politicians"]) <= 5

    def test_public_limit_param_is_ignored(self, client) -> None:
        data = client.get("/api/v1/politicians/incomplete?limit=50").get_json()["data"]

        assert data["limit"] == 5

    def test_service_token_lifts_cap(self, client, service_token) -> None:
        response = client.get(
            "/api/v1/politicians/incomplete?limit=8",
            headers={"X-Service-Token": service_token},
        )

        data = response.get_json()["data"]
        assert data["limit"] == 8
        assert data["daily_max"] is None
        assert len(data["politicians"]) == 8

    def test_bad_token_is_treated_as_public(self, client, service_token) -> None:
        data = client.get(
            "/api/v1/politicians/incomplete?limit=8",
            headers={"X-Service-Token": "wrong"},
        ).get_json()["data"]

        assert data["limit"] == 5


@pytest.mark.unit
class TestIngestRoute:
    _PID = "11111111-1111-1111-1111-111111111111"

    def test_requires_token(self, client, service_token) -> None:
        response = client.post(
            f"/api/v1/politicians/{self._PID}/ingest",
            json={"updates": {"contact": {"email": "a@example.com"}}},
        )

        assert response.status_code == 401
        assert response.get_json()["code"] == "SERVICE_TOKEN_INVALID"

    def test_unconfigured_token_returns_503(self, client, monkeypatch) -> None:
        monkeypatch.delenv("RAJNITI_SERVICE_TOKEN", raising=False)
        response = client.post(
            f"/api/v1/politicians/{self._PID}/ingest",
            json={"updates": {"contact": {"email": "a@example.com"}}},
            headers={"X-Service-Token": TOKEN},
        )

        assert response.status_code == 503
        assert response.get_json()["code"] == "SERVICE_TOKEN_NOT_CONFIGURED"

    def test_ingests_with_bearer_token(
        self, client, service_token, politician_service
    ) -> None:
        response = client.post(
            f"/api/v1/politicians/{self._PID}/ingest",
            json={"updates": {"contact": {"email": "a@example.com"}}},
            headers={"Authorization": "Bearer " + service_token},
        )

        assert response.status_code == 200
        assert response.get_json()["data"]["updated_fields"] == ["contact"]
        stored = politician_service.get_by_id(self._PID)
        assert stored["contact"]["email"] == "a@example.com"

    def test_rejects_non_ingestable_fields(self, client, service_token) -> None:
        response = client.post(
            f"/api/v1/politicians/{self._PID}/ingest",
            json={"updates": {"id": "other", "state": "Bihar"}},
            headers={"X-Service-Token": service_token},
        )

        assert response.status_code == 400
        assert "id" in response.get_json()["error"]

    def test_requires_updates_object(self, client, service_token) -> None:
        response = client.post(
            f"/api/v1/politicians/{self._PID}/ingest",
            json={},
            headers={"X-Service-Token": service_token},
        )

        assert response.status_code == 400

    def test_unknown_politician_returns_404(self, client, service_token) -> None:
        response = client.post(
            "/api/v1/politicians/00000000-0000-0000-0000-000000000000/ingest",
            json={"updates": {"contact": {"email": "a@example.com"}}},
            headers={"X-Service-Token": service_token},
        )

        assert response.status_code == 404
