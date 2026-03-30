"""
User service using Supabase (NO SQLite)
"""

from typing import Any, Dict, Optional
from app.core.supabase_client import supabase


class UserService:

    # =========================
    # CREATE OR GET USER
    # =========================
    def get_or_create_user(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user_id = user_info.get("id") or user_info.get("sub")
            email = user_info.get("email")
            name = user_info.get("name")
            picture = user_info.get("profile_picture") or user_info.get("picture")

            if not user_id or not email:
                raise ValueError("User ID and email are required")

            # 🔍 check if exists
            res = supabase.table("users").select("*").eq("id", user_id).execute()

            if res.data:
                return res.data[0]

            # 🆕 insert user
            new_user = {
                "id": str(user_id),
                "email": email,
                "name": name,
                "profile_picture": picture,
                "onboarding_completed": False,
            }
            res = supabase.table("users").insert(new_user).execute()
            print("🟢 INSERT RESULT:", res)

            return new_user

        except Exception as e:
            print("❌ ERROR in get_or_create_user:", e)
            raise e

    # =========================
    # GET USER
    # =========================
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            res = supabase.table("users").select("*").eq("id", user_id).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print("❌ ERROR get_user:", e)
            return None

    # =========================
    # UPDATE USER
    # =========================
    def update_user_profile(self, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        try:
            if not kwargs:
                return None

            #  fix array issue
            if "preferred_parties" in kwargs and isinstance(kwargs["preferred_parties"], list):
                kwargs["preferred_parties"] = ", ".join(kwargs["preferred_parties"])

            if "topics_of_interest" in kwargs and isinstance(kwargs["topics_of_interest"], list):
                kwargs["topics_of_interest"] = ", ".join(kwargs["topics_of_interest"])

            supabase.table("users").update(kwargs).eq("id", user_id).execute()

            return self.get_user_by_id(user_id)

        except Exception as e:
            print("❌ ERROR update_user:", e)
            return None

    # =========================
    # USERNAME CHECK
    # =========================
    def check_username_available(self, username, exclude_user_id=None):
        try:
            if not username:
              return False

              res = supabase.table("users").select("id").eq("username", username).execute()

              print("DEBUG USERNAME RES:", res)

              if not hasattr(res, "data") or res.data is None:
               return True

              if len(res.data) == 0:
               return True

              if exclude_user_id and res.data[0]["id"] == exclude_user_id:
               return True

              return False

        except Exception as e:
              print("❌ USERNAME ERROR:", e)
        return True