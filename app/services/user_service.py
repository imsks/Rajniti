"""
User service for managing user data operations.
No authentication logic - only data operations.
"""

from typing import Any, Dict, Optional

from app.database import get_db_session
from app.database.models import User


class UserService:
    """Service for handling user data operations."""

    def get_or_create_user(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get existing user or create a new one from user info.

        Args:
            user_info: User information (from NextAuth)
                - id: User ID (Google user ID)
                - email: User email
                - name: User's full name
                - profile_picture: URL to profile picture

        Returns:
            User dictionary
        """
        with get_db_session() as session:
            user_id = user_info.get("id") or user_info.get(
                "sub"
            )  # Support both formats
            email = user_info.get("email")
            name = user_info.get("name")
            picture = user_info.get("profile_picture") or user_info.get("picture")

            if not user_id or not email:
                raise ValueError("User ID and email are required")

            # Check if user exists
            user = User.get_by_id(session, user_id)

            if not user:
                # Create new user
                user = User.create(
                    session=session,
                    id=user_id,
                    email=email,
                    name=name,
                    profile_picture=picture,
                )
            else:
                # Update profile picture if changed
                if picture and user.profile_picture != picture:
                    user.update(session, profile_picture=picture)
                # Update name if changed
                if name and user.name != name:
                    user.update(session, name=name)

            return user.to_dict()

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User dictionary or None if not found
        """
        with get_db_session() as session:
            user = User.get_by_id(session, user_id)
            return user.to_dict() if user else None

    def update_user_profile(self, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Update user profile information.

        Args:
            user_id: User ID
            **kwargs: Fields to update

        Returns:
            Updated user dictionary or None if user not found
        """
        with get_db_session() as session:
            user = User.get_by_id(session, user_id)
            if not user:
                return None

            # Handle username update specially (uniqueness check should be done by controller/route)
            # But we can double check here if needed or trust the controller.
            # For simplicity, we assume controller checked availability.

            # Update fields
            user.update(session, **kwargs)
            return user.to_dict()

    def check_username_available(
        self, username: str, exclude_user_id: Optional[str] = None
    ) -> bool:
        """
        Check if username is available.

        Args:
            username: Username to check
            exclude_user_id: User ID to exclude from check (for updating own username)

        Returns:
            True if username is available, False otherwise
        """
        with get_db_session() as session:
            user = User.get_by_username(session, username)
            if not user:
                return True
            # If checking for a specific user, allow them to keep their own username
            if exclude_user_id and user.id == exclude_user_id:
                return True
            return False
