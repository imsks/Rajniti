"""Tests for the service-token helper used by ingestion routes."""

import pytest
from flask import Flask

from app.core.service_auth import has_valid_service_token, require_service_token


@pytest.fixture
def token_app() -> Flask:
    app = Flask(__name__)

    @app.route("/guarded", methods=["POST"])
    @require_service_token
    def guarded():
        return {"ok": True}

    @app.route("/probe", methods=["GET"])
    def probe():
        return {"valid": has_valid_service_token()}

    return app


@pytest.mark.unit
class TestServiceAuth:
    def test_probe_false_without_token(self, token_app, monkeypatch) -> None:
        monkeypatch.delenv("RAJNITI_SERVICE_TOKEN", raising=False)
        with token_app.test_client() as c:
            assert c.get("/probe").get_json()["valid"] is False

    def test_probe_true_with_matching_header(self, token_app, monkeypatch) -> None:
        monkeypatch.setenv("RAJNITI_SERVICE_TOKEN", "abc123")
        with token_app.test_client() as c:
            response = c.get("/probe", headers={"X-Service-Token": "abc123"})
            assert response.get_json()["valid"] is True

    def test_probe_false_for_mismatched_token(self, token_app, monkeypatch) -> None:
        monkeypatch.setenv("RAJNITI_SERVICE_TOKEN", "abc123")
        with token_app.test_client() as c:
            response = c.get("/probe", headers={"X-Service-Token": "nope"})
            assert response.get_json()["valid"] is False

    def test_guard_rejects_missing_token(self, token_app, monkeypatch) -> None:
        monkeypatch.setenv("RAJNITI_SERVICE_TOKEN", "abc123")
        with token_app.test_client() as c:
            assert c.post("/guarded").status_code == 401

    def test_guard_allows_bearer_token(self, token_app, monkeypatch) -> None:
        monkeypatch.setenv("RAJNITI_SERVICE_TOKEN", "abc123")
        with token_app.test_client() as c:
            response = c.post(
                "/guarded", headers={"Authorization": "Bearer " + "abc123"}
            )
            assert response.status_code == 200

    def test_guard_503_when_unconfigured(self, token_app, monkeypatch) -> None:
        monkeypatch.delenv("RAJNITI_SERVICE_TOKEN", raising=False)
        with token_app.test_client() as c:
            response = c.post("/guarded", headers={"X-Service-Token": "abc123"})
            assert response.status_code == 503
