"""
User service backed by PostgreSQL (DATABASE_URL), including Supabase Postgres.
"""

from sqlalchemy import text
from typing import Any, Dict, Optional

from app.database.base import get_db_session
from app.database.models.user import User


class UserService:
    def get_or_create_user(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        user_id = user_info.get("id") or user_info.get("sub")
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("profile_picture") or user_info.get("picture")

        if not user_id or not email:
            raise ValueError("User ID and email are required")

        with get_db_session() as session:
            existing = User.get_by_id(session, str(user_id))
            if existing:
                updates: Dict[str, Any] = {}
                if picture is not None and existing.profile_picture != picture:
                    updates["profile_picture"] = picture
                if name is not None and existing.name != name:
                    updates["name"] = name
                if updates:
                    existing.update(session, **updates)
                return existing.to_dict()

            user = User.create(
                session,
                id=str(user_id),
                email=email,
                name=name,
                profile_picture=picture,
            )
            return user.to_dict()

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            with get_db_session() as session:
                user = User.get_by_id(session, user_id)
                return user.to_dict() if user else None
        except Exception as e:
            print("❌ ERROR get_user:", e)
            return None

    def update_user_profile(self, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        if not kwargs:
            return None

        with get_db_session() as session:
            user = User.get_by_id(session, user_id)
            if not user:
                return None
            user.update(session, **kwargs)
            return user.to_dict()

    def check_username_available(self, username, exclude_user_id=None):
        if not username:
            return False

        with get_db_session() as session:
            existing = User.get_by_username(session, username)
            if existing is None:
                return True
            if exclude_user_id and existing.id == exclude_user_id:
                return True
            return False

    # ==================== USER POLITICIANS ====================

    def add_user_politician(self, user_id: str, politician_id: str, role: str):
        try:
            with get_db_session() as session:
                session.execute(
                    text("""
                        INSERT INTO user_politicians (user_id, politician_id, role)
                        VALUES (:user_id, :politician_id, :role)
                        ON CONFLICT (user_id, role)
                        DO UPDATE SET politician_id = EXCLUDED.politician_id
                        """),
                    {
                        "user_id": user_id,
                        "politician_id": politician_id,
                        "role": role,
                    },
                )
                session.commit()
                return {"success": True}
        except Exception as e:
            print("❌ ERROR add_user_politician:", e)
            return None

    def get_user_politicians(self, user_id: str):
        try:
            with get_db_session() as session:
                result = session.execute(
                    text("SELECT * FROM user_politicians WHERE user_id = :user_id"),
                    {"user_id": user_id},
                )
                return [dict(row._mapping) for row in result]
        except Exception as e:
            print("❌ ERROR get_user_politicians:", e)
            return []

    def remove_user_politician(self, user_id: str, politician_id: str):
        try:
            with get_db_session() as session:
                session.execute(
                    text(
                        "DELETE FROM user_politicians WHERE user_id = :user_id AND politician_id = :politician_id"
                    ),
                    {
                        "user_id": user_id,
                        "politician_id": politician_id,
                    },
                )
                session.commit()
                return {"deleted": True}
        except Exception as e:
            print("❌ ERROR remove_user_politician:", e)
            return False
