"""Integration tests for user politician persistence (real SQL, in-memory SQLite)."""

from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.services.user_service import UserService


@pytest.fixture
def user_politician_service(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE users (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE user_politicians (
                    user_id TEXT NOT NULL,
                    politician_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, role),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
        )
        conn.execute(
            text("INSERT INTO users (id, email) VALUES ('user-1', 'user@test.local')")
        )

    @contextmanager
    def _session():
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    monkeypatch.setattr("app.services.user_service.get_db_session", _session)
    return UserService()


@pytest.mark.integration
class TestUserPoliticiansRoundtrip:
    def test_add_get_and_remove_politician(self, user_politician_service):
        svc = user_politician_service

        assert svc.get_user_politicians("user-1") == []

        added = svc.add_user_politician("user-1", "pol-1", "MP")
        assert added == {"success": True}

        saved = svc.get_user_politicians("user-1")
        assert len(saved) == 1
        assert saved[0]["politician_id"] == "pol-1"
        assert saved[0]["role"] == "MP"

        replaced = svc.add_user_politician("user-1", "pol-2", "MP")
        assert replaced == {"success": True}

        updated = svc.get_user_politicians("user-1")
        assert len(updated) == 1
        assert updated[0]["politician_id"] == "pol-2"

        removed = svc.remove_user_politician("user-1", "pol-2")
        assert removed == {"deleted": True}
        assert svc.get_user_politicians("user-1") == []

    def test_add_mla_and_mp_for_same_user(self, user_politician_service):
        svc = user_politician_service

        assert svc.add_user_politician("user-1", "mp-1", "MP") == {"success": True}
        assert svc.add_user_politician("user-1", "mla-1", "MLA") == {"success": True}

        saved = svc.get_user_politicians("user-1")
        roles = {row["role"]: row["politician_id"] for row in saved}

        assert roles == {"MP": "mp-1", "MLA": "mla-1"}


@pytest.mark.integration
class TestUserPoliticiansHttpRoundtrip:
    def test_http_add_get_delete_roundtrip(self, client, user_politician_service):
        with patch(
            "app.routes.user_routes.get_user_service",
            return_value=user_politician_service,
        ):
            empty = client.get("/api/v1/users/user-1/politicians")
            assert empty.status_code == 200
            assert empty.get_json()["data"] == []

            added = client.post(
                "/api/v1/users/user-1/politicians",
                json={"politician_id": "pol-1", "role": "MP"},
            )
            assert added.status_code == 200
            assert added.get_json()["success"] is True

            fetched = client.get("/api/v1/users/user-1/politicians")
            assert fetched.status_code == 200
            data = fetched.get_json()["data"]
            assert len(data) == 1
            assert data[0]["politician_id"] == "pol-1"
            assert data[0]["role"] == "MP"

            deleted = client.delete("/api/v1/users/user-1/politicians/pol-1")
            assert deleted.status_code == 200
            assert deleted.get_json()["success"] is True

            after_delete = client.get("/api/v1/users/user-1/politicians")
            assert after_delete.get_json()["data"] == []

    def test_http_upsert_replaces_existing_mp(self, client, user_politician_service):
        with patch(
            "app.routes.user_routes.get_user_service",
            return_value=user_politician_service,
        ):
            client.post(
                "/api/v1/users/user-1/politicians",
                json={"politician_id": "pol-1", "role": "MP"},
            )
            client.post(
                "/api/v1/users/user-1/politicians",
                json={"politician_id": "pol-2", "role": "MP"},
            )

            fetched = client.get("/api/v1/users/user-1/politicians")
            data = fetched.get_json()["data"]
            assert len(data) == 1
            assert data[0]["politician_id"] == "pol-2"
