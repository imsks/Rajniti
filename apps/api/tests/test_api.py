import pytest


@pytest.mark.integration
def test_health_ok(client) -> None:
    resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


@pytest.mark.integration
def test_get_rep(client) -> None:
    resp = client.get("/api/v1/reps/mp-123")

    assert resp.status_code == 200
    assert resp.get_json()["id"] == "mp-123"


@pytest.mark.integration
def test_get_rep_promises(client) -> None:
    resp = client.get("/api/v1/reps/mp-123/promises")

    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
