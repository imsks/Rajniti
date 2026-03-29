"""
User routes for user data management.
"""

from flask import Blueprint, jsonify, request

user_bp = Blueprint("user", __name__, url_prefix="/api/v1/users")

user_service = None

def get_user_service():
    global user_service
    if user_service is None:
        from app.services.user_service import UserService
        user_service = UserService()
    return user_service


# ==================== USER ROUTES ====================

@user_bp.route("/sync", methods=["POST"])
def sync_user():
    """
    Called by NextAuth on every Google login.
    MUST return onboarding_completed so JWT token gets it.
    """
    try:
        data = request.get_json()

        user_info = {
            "id":              data.get("id"),
            "email":           data.get("email"),
            "name":            data.get("name"),
            "profile_picture": data.get("profile_picture"),
        }

        if not user_info["id"] or not user_info["email"]:
            return jsonify({"success": False, "error": "id and email are required"}), 400

        user = get_user_service().get_or_create_user(user_info)

        return jsonify({
            "success": True,
            "data": user  # includes onboarding_completed
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@user_bp.route("/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = get_user_service().get_user_by_id(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        return jsonify({"success": True, "data": user})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@user_bp.route("/<user_id>", methods=["PATCH", "PUT"])
def update_user(user_id):
    try:
        data = request.get_json()

        username = data.get("username")
        if username:
            is_available = get_user_service().check_username_available(
                username, exclude_user_id=user_id
            )
            if not is_available:
                return jsonify({"success": False, "error": "Username is already taken"}), 400

        allowed_fields = [
            "name",
            "phone",                # ← NEW
            "state",
            "city",
            "age_group",
            "pincode",
            "profile_picture",
            "username",
            "political_ideology",
            "preferred_parties",    # ← NEW
            "topics_of_interest",   # ← NEW
            "onboarding_completed",
        ]

        update_data = {
            key: value
            for key, value in data.items()
            if key in allowed_fields
        }

        updated_user = get_user_service().update_user_profile(user_id, **update_data)

        if not updated_user:
            return jsonify({"success": False, "error": "User not found"}), 404

        return jsonify({
            "success": True,
            "data": updated_user,
            "message": "User updated successfully",
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@user_bp.route("/check-username", methods=["POST"])
def check_username():
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        user_id  = data.get("user_id")

        if not username:
            return jsonify({"success": False, "error": "Username is required"}), 400

        is_available = get_user_service().check_username_available(
            username, exclude_user_id=user_id
        )
        return jsonify({"success": True, "available": is_available})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== HEALTH CHECK ====================

@user_bp.route("/health", methods=["GET"])
def user_health():
    return jsonify({
        "success": True,
        "service": "User Service",
        "message": "User service is operational",
    })