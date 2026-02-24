"""
Unit tests for UserService.

Tests cover user operations, onboarding, and username validation.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb before imports
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()

from app.services.user_service import UserService


@pytest.fixture
def user_service():
    """Create a UserService instance."""
    return UserService()


@pytest.mark.unit
class TestGetOrCreateUser:
    """Tests for get_or_create_user method."""

    def test_create_new_user(self, user_service, sample_user_data):
        """Test creating a new user when user doesn't exist."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            # User doesn't exist
            with patch("app.database.models.User.get_by_id", return_value=None):
                mock_user = Mock()
                mock_user.to_dict.return_value = sample_user_data

                with patch("app.database.models.User.create", return_value=mock_user):
                    result = user_service.get_or_create_user(
                        {
                            "id": sample_user_data["id"],
                            "email": sample_user_data["email"],
                            "name": sample_user_data["name"],
                            "profile_picture": sample_user_data["profile_picture"],
                        }
                    )

                    assert result == sample_user_data

    def test_get_existing_user(self, user_service, sample_user_data):
        """Test returning existing user."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            # User exists
            mock_user = Mock()
            mock_user.to_dict.return_value = sample_user_data
            mock_user.profile_picture = sample_user_data["profile_picture"]
            mock_user.name = sample_user_data["name"]

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                result = user_service.get_or_create_user(
                    {"id": sample_user_data["id"], "email": sample_user_data["email"]}
                )

                assert result == sample_user_data

    def test_update_profile_picture_on_login(self, user_service, sample_user_data):
        """Test profile picture is updated on login if changed."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.profile_picture = "old_picture.jpg"
            mock_user.name = sample_user_data["name"]
            mock_user.to_dict.return_value = sample_user_data
            mock_user.update = Mock()

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                user_service.get_or_create_user(
                    {
                        "id": sample_user_data["id"],
                        "email": sample_user_data["email"],
                        "profile_picture": "new_picture.jpg",
                    }
                )

                mock_user.update.assert_called()

    def test_missing_required_fields_raises_error(self, user_service):
        """Test that missing required fields raises ValueError."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            with pytest.raises(ValueError) as exc_info:
                user_service.get_or_create_user(
                    {"name": "Test"}
                )  # Missing id and email

            assert "required" in str(exc_info.value).lower()

    def test_supports_sub_field_for_id(self, user_service, sample_user_data):
        """Test that 'sub' field is accepted as user ID."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.to_dict.return_value = sample_user_data
            mock_user.profile_picture = None
            mock_user.name = None

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                result = user_service.get_or_create_user(
                    {
                        "sub": sample_user_data["id"],  # Using 'sub' instead of 'id'
                        "email": sample_user_data["email"],
                    }
                )

                assert result is not None


@pytest.mark.unit
class TestGetUserById:
    """Tests for get_user_by_id method."""

    def test_get_user_found(self, user_service, sample_user_data):
        """Test getting user when found."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.to_dict.return_value = sample_user_data

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                result = user_service.get_user_by_id("test-user-123")

                assert result == sample_user_data

    def test_get_user_not_found(self, user_service):
        """Test getting user when not found."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            with patch("app.database.models.User.get_by_id", return_value=None):
                result = user_service.get_user_by_id("nonexistent")

                assert result is None


@pytest.mark.unit
class TestUpdateUserProfile:
    """Tests for update_user_profile method."""

    def test_update_success(self, user_service, sample_user_data):
        """Test successful profile update."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            updated_data = sample_user_data.copy()
            updated_data["name"] = "Updated Name"

            mock_user = Mock()
            mock_user.update = Mock()
            mock_user.to_dict.return_value = updated_data

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                result = user_service.update_user_profile(
                    "test-user-123", name="Updated Name"
                )

                assert result["name"] == "Updated Name"
                mock_user.update.assert_called_once()

    def test_update_user_not_found(self, user_service):
        """Test update when user not found."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            with patch("app.database.models.User.get_by_id", return_value=None):
                result = user_service.update_user_profile(
                    "nonexistent", name="New Name"
                )

                assert result is None

    def test_update_multiple_fields(self, user_service, sample_user_data):
        """Test updating multiple fields at once."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.update = Mock()
            mock_user.to_dict.return_value = sample_user_data

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                user_service.update_user_profile(
                    "test-user-123",
                    name="New Name",
                    state="MH",
                    city="Mumbai",
                    political_ideology="Centrist",
                )

                mock_user.update.assert_called_once()
                call_kwargs = mock_user.update.call_args[1]
                assert "name" in call_kwargs
                assert "state" in call_kwargs
                assert "city" in call_kwargs


@pytest.mark.unit
class TestCheckUsernameAvailable:
    """Tests for check_username_available method."""

    def test_username_available(self, user_service):
        """Test username is available."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            with patch("app.database.models.User.get_by_username", return_value=None):
                result = user_service.check_username_available("newusername")

                assert result is True

    def test_username_taken(self, user_service, mock_user):
        """Test username is taken."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            with patch(
                "app.database.models.User.get_by_username", return_value=mock_user
            ):
                result = user_service.check_username_available("testuser")

                assert result is False

    def test_username_available_for_same_user(self, user_service):
        """Test username is available when checking own username."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.id = "test-user-123"

            with patch(
                "app.database.models.User.get_by_username", return_value=mock_user
            ):
                # Same user checking their own username should return True
                result = user_service.check_username_available(
                    "testuser", exclude_user_id="test-user-123"
                )

                assert result is True

    def test_username_taken_by_different_user(self, user_service):
        """Test username is taken by different user."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.id = "different-user"

            with patch(
                "app.database.models.User.get_by_username", return_value=mock_user
            ):
                # Different user has this username
                result = user_service.check_username_available(
                    "testuser", exclude_user_id="test-user-123"
                )

                assert result is False


@pytest.mark.unit
class TestUserServiceEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_user_info(self, user_service):
        """Test handling empty user info."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            with pytest.raises(ValueError):
                user_service.get_or_create_user({})

    def test_profile_picture_variations(self, user_service, sample_user_data):
        """Test different profile picture field names."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            mock_user = Mock()
            mock_user.to_dict.return_value = sample_user_data
            mock_user.profile_picture = None
            mock_user.name = None
            mock_user.update = Mock()

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                # Test 'picture' field name (OAuth style)
                user_service.get_or_create_user(
                    {
                        "id": sample_user_data["id"],
                        "email": sample_user_data["email"],
                        "picture": "https://example.com/pic.jpg",
                    }
                )

                # Should handle both 'profile_picture' and 'picture' fields

    def test_username_with_special_characters(self, user_service):
        """Test username availability check with special characters."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            with patch("app.database.models.User.get_by_username", return_value=None):
                result = user_service.check_username_available("user_123")
                assert result is True

    def test_onboarding_completion(self, user_service, sample_user_data):
        """Test updating onboarding_completed flag."""
        with patch("app.services.user_service.get_db_session") as mock_session_ctx:
            mock_session = Mock()
            mock_session_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_session_ctx.return_value.__exit__ = Mock(return_value=False)

            updated_data = sample_user_data.copy()
            updated_data["onboarding_completed"] = True

            mock_user = Mock()
            mock_user.update = Mock()
            mock_user.to_dict.return_value = updated_data

            with patch("app.database.models.User.get_by_id", return_value=mock_user):
                result = user_service.update_user_profile(
                    "test-user-123", onboarding_completed=True
                )

                assert result["onboarding_completed"] is True
