import pytest

from app import create_app
from app.core.config import Settings


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


@pytest.mark.integration
def test_secret_key_is_applied_to_flask_config() -> None:
    """Flask signs sessions with app.config["SECRET_KEY"], not our Settings object."""
    app = create_app(Settings(flask_env="testing", secret_key="s3cret"))

    assert app.config["SECRET_KEY"] == "s3cret"


@pytest.mark.integration
def test_production_rejects_placeholder_secret_key() -> None:
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app(Settings(flask_env="production"))


@pytest.mark.integration
def test_production_accepts_real_secret_key() -> None:
    app = create_app(Settings(flask_env="production", secret_key="a-real-one"))

    assert app.config["SECRET_KEY"] == "a-real-one"
