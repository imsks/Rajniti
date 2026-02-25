"""
Integration tests for user-related routes.

Tests verify user endpoints work correctly including auth sync and profile updates.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb before imports
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()


@pytest.mark.integration
class TestUserSync:
    """Tests for user sync endpoint."""

    def test_sync_user_success(self, client, sample_user_data):
        """Test successful user sync."""
        with patch("app.services.user_service.get_db_session") as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.to_dict.return_value = sample_user_data
            mock_user.profile_picture = sample_user_data["profile_picture"]
            mock_user.name = sample_user_data["name"]

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                response = client.post(
                    "/api/v1/users/sync",
                    json={
                        "id": sample_user_data["id"],
                        "email": sample_user_data["email"],
                        "name": sample_user_data["name"],
                        "profile_picture": sample_user_data["profile_picture"],
                    },
                )

                assert response.status_code == 200
                data = response.get_json()
                assert data["success"] is True

    def test_sync_user_missing_id(self, client):
        """Test sync user without ID."""
        response = client.post("/api/v1/users/sync", json={"email": "test@example.com"})

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_sync_user_missing_email(self, client):
        """Test sync user without email."""
        response = client.post("/api/v1/users/sync", json={"id": "test-123"})

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_sync_user_creates_new(self, client, sample_user_data):
        """Test sync creates new user if not exists."""
        with patch("app.services.user_service.get_db_session") as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.to_dict.return_value = sample_user_data

            with patch("app.database.models.User.get_by_id", return_value=None):
                with patch("app.database.models.User.create", return_value=mock_user):
                    response = client.post(
                        "/api/v1/users/sync",
                        json={
                            "id": sample_user_data["id"],
                            "email": sample_user_data["email"],
                        },
                    )

                    assert response.status_code == 200


@pytest.mark.integration
class TestGetUser:
    """Tests for get user endpoint."""

    def test_get_user_success(self, client, sample_user_data):
        """Test getting user by ID."""
        with patch("app.services.user_service.get_db_session") as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.to_dict.return_value = sample_user_data

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                response = client.get(f'/api/v1/users/{sample_user_data["id"]}')

                assert response.status_code == 200
                data = response.get_json()
                assert data["success"] is True

    def test_get_user_not_found(self, client):
        """Test getting non-existent user."""
        with patch("app.services.user_service.get_db_session") as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            with patch("app.database.models.User.get_by_id", return_value=None):
                response = client.get("/api/v1/users/nonexistent")

                assert response.status_code == 404


@pytest.mark.integration
class TestUpdateUser:
    """Tests for update user endpoint."""

    def test_update_user_success(self, client, sample_user_data):
        """Test updating user profile."""
        with patch("app.services.user_service.get_db_session") as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.id = sample_user_data["id"]
            updated_data = sample_user_data.copy()
            updated_data["name"] = "Updated Name"
            mock_user.to_dict.return_value = updated_data
            mock_user.update = Mock()

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                with patch(
                    "app.database.models.User.get_by_username", return_value=None
                ):
                    response = client.patch(
                        f'/api/v1/users/{sample_user_data["id"]}',
                        json={"name": "Updated Name"},
                    )

                    assert response.status_code == 200

    def test_update_user_not_found(self, client):
        """Test updating non-existent user."""
        with patch("app.services.user_service.get_db_session") as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            with patch("app.database.models.User.get_by_id", return_value=None):
                response = client.patch(
                    "/api/v1/users/nonexistent", json={"name": "Test"}
                )

                assert response.status_code == 404

    def test_update_user_username_taken(self, client, sample_user_data):
        """Test updating user with taken username."""
        with patch("app.services.user_service.get_db_session") as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.id = sample_user_data["id"]

            # Another user has the username
            other_user = Mock()
            other_user.id = "other-user-id"

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                with patch(
                    "app.database.models.User.get_by_username", return_value=other_user
                ):
                    response = client.patch(
                        f'/api/v1/users/{sample_user_data["id"]}',
                        json={"username": "taken_username"},
                    )

                    assert response.status_code == 400
                    data = response.get_json()
                    assert "taken" in data["error"].lower()

    def test_update_user_onboarding_complete(self, client, sample_user_data):
        """Test completing user onboarding."""
        with patch("app.services.user_service.get_db_session") as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.id = sample_user_data["id"]
            updated_data = sample_user_data.copy()
            updated_data["onboarding_completed"] = True
            mock_user.to_dict.return_value = updated_data
            mock_user.update = Mock()

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                with patch(
                    "app.database.models.User.get_by_username", return_value=None
                ):
                    response = client.patch(
                        f'/api/v1/users/{sample_user_data["id"]}',
                        json={
                            "username": "newuser",
                            "state": "DL",
                            "city": "Delhi",
                            "onboarding_completed": True,
                        },
                    )

                    assert response.status_code == 200

    def test_update_user_put_method(self, client, sample_user_data):
        """Test update works with PUT method too."""
        with patch("app.services.user_service.get_db_session") as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.id = sample_user_data["id"]
            mock_user.to_dict.return_value = sample_user_data
            mock_user.update = Mock()

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                with patch(
                    "app.database.models.User.get_by_username", return_value=None
                ):
                    response = client.put(
                        f'/api/v1/users/{sample_user_data["id"]}', json={"name": "Test"}
                    )

                    assert response.status_code == 200


@pytest.mark.integration
class TestCheckUsername:
    """Tests for username availability check endpoint."""

    def test_check_username_available(self, client):
        """Test checking available username."""
        with patch("app.services.user_service.get_db_session") as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            with patch("app.database.models.User.get_by_username", return_value=None):
                response = client.post(
                    "/api/v1/users/check-username",
                    json={"username": "available_username"},
                )

                assert response.status_code == 200
                data = response.get_json()
                assert data["success"] is True
                assert data["available"] is True

    def test_check_username_taken(self, client):
        """Test checking taken username."""
        with patch("app.services.user_service.get_db_session") as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.id = "other-user"

            with patch(
                "app.database.models.User.get_by_username", return_value=mock_user
            ):
                response = client.post(
                    "/api/v1/users/check-username", json={"username": "taken_username"}
                )

                assert response.status_code == 200
                data = response.get_json()
                assert data["available"] is False

    def test_check_username_missing(self, client):
        """Test checking username without providing one."""
        response = client.post("/api/v1/users/check-username", json={})

        assert response.status_code == 400

    def test_check_username_empty(self, client):
        """Test checking empty username."""
        response = client.post("/api/v1/users/check-username", json={"username": ""})

        assert response.status_code == 400

    def test_check_username_exclude_self(self, client, sample_user_data):
        """Test checking username excluding current user."""
        with patch("app.services.user_service.get_db_session") as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            # User checking their own username
            mock_user = Mock()
            mock_user.id = sample_user_data["id"]

            with patch(
                "app.database.models.User.get_by_username", return_value=mock_user
            ):
                response = client.post(
                    "/api/v1/users/check-username",
                    json={"username": "my_username", "user_id": sample_user_data["id"]},
                )

                assert response.status_code == 200
                data = response.get_json()
                # Should be available since it's their own username
                assert data["available"] is True


@pytest.mark.integration
class TestUserHealth:
    """Tests for user service health endpoint."""

    def test_user_health_endpoint(self, client):
        """Test user service health check."""
        response = client.get("/api/v1/users/health")

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "User Service" in data["service"]
