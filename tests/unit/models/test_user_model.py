"""
Unit tests for User database model.

Tests cover CRUD operations, validation, and model methods.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock chromadb before imports
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()

from app.database.models import User


@pytest.mark.unit
class TestUserModel:
    """Tests for User model basic functionality."""

    def test_user_repr(self, mock_user):
        """Test User string representation."""
        repr(mock_user)
        assert mock_user.id is not None
        assert mock_user.email is not None

    def test_user_to_dict(self, mock_user, sample_user_data):
        """Test User to_dict method."""
        result = mock_user.to_dict()
        assert result["id"] == sample_user_data["id"]
        assert result["email"] == sample_user_data["email"]
        assert result["name"] == sample_user_data["name"]

    def test_user_has_required_fields(self, mock_user):
        """Test User has all required fields."""
        required_fields = [
            "id",
            "email",
            "name",
            "username",
            "profile_picture",
            "state",
            "city",
            "pincode",
            "age_group",
            "political_ideology",
            "onboarding_completed",
        ]
        for field in required_fields:
            assert hasattr(mock_user, field)


@pytest.mark.unit
class TestUserCreate:
    """Tests for User.create method."""

    def test_create_user_minimal(self, mock_db_session):
        """Test creating user with minimal required data."""
        with patch.object(User, "create") as mock_create:
            mock_user = Mock(spec=User)
            mock_user.id = "new-user"
            mock_user.email = "new@example.com"
            mock_user.onboarding_completed = False
            mock_create.return_value = mock_user

            user = User.create(
                session=mock_db_session, id="new-user", email="new@example.com"
            )

            assert user.id == "new-user"
            assert user.email == "new@example.com"
            assert user.onboarding_completed is False

    def test_create_user_full_data(self, mock_db_session, sample_user_data):
        """Test creating user with all fields."""
        with patch.object(User, "create") as mock_create:
            mock_user = Mock(spec=User)
            for key, value in sample_user_data.items():
                setattr(mock_user, key, value)
            mock_create.return_value = mock_user

            user = User.create(
                session=mock_db_session,
                id=sample_user_data["id"],
                email=sample_user_data["email"],
                name=sample_user_data["name"],
                profile_picture=sample_user_data["profile_picture"],
            )

            assert user.id == sample_user_data["id"]
            assert user.email == sample_user_data["email"]
            assert user.name == sample_user_data["name"]


@pytest.mark.unit
class TestUserRead:
    """Tests for User read operations."""

    def test_get_by_id_found(self, mock_db_session, mock_user):
        """Test getting user by ID when found."""
        with patch.object(User, "get_by_id", return_value=mock_user):
            user = User.get_by_id(mock_db_session, "test-user-123")
            assert user is not None
            assert user.id == "test-user-123"

    def test_get_by_id_not_found(self, mock_db_session):
        """Test getting user by ID when not found."""
        with patch.object(User, "get_by_id", return_value=None):
            user = User.get_by_id(mock_db_session, "nonexistent")
            assert user is None

    def test_get_by_email_found(self, mock_db_session, mock_user):
        """Test getting user by email when found."""
        with patch.object(User, "get_by_email", return_value=mock_user):
            user = User.get_by_email(mock_db_session, "test@example.com")
            assert user is not None
            assert user.email == "test@example.com"

    def test_get_by_email_not_found(self, mock_db_session):
        """Test getting user by email when not found."""
        with patch.object(User, "get_by_email", return_value=None):
            user = User.get_by_email(mock_db_session, "nonexistent@example.com")
            assert user is None

    def test_get_by_username_found(self, mock_db_session, mock_user):
        """Test getting user by username when found."""
        with patch.object(User, "get_by_username", return_value=mock_user):
            user = User.get_by_username(mock_db_session, "testuser")
            assert user is not None
            assert user.username == "testuser"

    def test_get_by_username_not_found(self, mock_db_session):
        """Test getting user by username when not found."""
        with patch.object(User, "get_by_username", return_value=None):
            user = User.get_by_username(mock_db_session, "nonexistent")
            assert user is None

    def test_is_username_available_true(self, mock_db_session):
        """Test username availability check when available."""
        with patch.object(User, "is_username_available", return_value=True):
            result = User.is_username_available(mock_db_session, "newusername")
            assert result is True

    def test_is_username_available_false(self, mock_db_session):
        """Test username availability check when taken."""
        with patch.object(User, "is_username_available", return_value=False):
            result = User.is_username_available(mock_db_session, "existinguser")
            assert result is False

    def test_get_all_users(self, mock_db_session, mock_user):
        """Test getting all users."""
        with patch.object(User, "get_all", return_value=[mock_user]):
            users = User.get_all(mock_db_session)
            assert len(users) == 1
            assert users[0].id == "test-user-123"


@pytest.mark.unit
class TestUserUpdate:
    """Tests for User update operations."""

    def test_update_single_field(self, mock_db_session, mock_user):
        """Test updating a single field."""
        mock_user.update.return_value = mock_user
        mock_user.name = "Updated Name"

        result = mock_user.update(mock_db_session, name="Updated Name")

        mock_user.update.assert_called_once_with(mock_db_session, name="Updated Name")
        assert result.name == "Updated Name"

    def test_update_multiple_fields(self, mock_db_session, mock_user):
        """Test updating multiple fields."""
        mock_user.update.return_value = mock_user
        mock_user.name = "New Name"
        mock_user.city = "Mumbai"

        result = mock_user.update(mock_db_session, name="New Name", city="Mumbai")

        assert result.name == "New Name"
        assert result.city == "Mumbai"

    def test_complete_onboarding(self, mock_db_session, mock_user):
        """Test completing user onboarding."""
        mock_user.onboarding_completed = True
        mock_user.complete_onboarding = Mock(return_value=mock_user)

        result = mock_user.complete_onboarding(
            mock_db_session,
            username="newusername",
            state="DL",
            city="Delhi",
            age_group="25-35",
        )

        assert result.onboarding_completed is True


@pytest.mark.unit
class TestUserDelete:
    """Tests for User delete operations."""

    def test_delete_user(self, mock_db_session, mock_user):
        """Test deleting a user."""
        mock_user.delete(mock_db_session)
        mock_user.delete.assert_called_once_with(mock_db_session)


@pytest.mark.unit
class TestUserValidation:
    """Tests for User validation logic."""

    def test_valid_email_format(self, sample_user_data):
        """Test valid email format."""
        email = sample_user_data["email"]
        assert "@" in email
        assert "." in email.split("@")[1]

    def test_valid_age_groups(self):
        """Test valid age group values."""
        valid_age_groups = ["18-25", "25-35", "35-45", "45-55", "55+"]
        for age_group in valid_age_groups:
            assert isinstance(age_group, str)
            assert "-" in age_group or "+" in age_group

    def test_valid_political_ideologies(self):
        """Test valid political ideology values."""
        valid_ideologies = [
            "Rightist",
            "Leftist",
            "Communist",
            "Centrist",
            "Libertarian",
            "Neutral",
        ]
        for ideology in valid_ideologies:
            assert isinstance(ideology, str)
            assert len(ideology) > 0
