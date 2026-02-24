"""
User routes for user data management.
No authentication logic - NextAuth handles authentication.
Backend only provides user data operations.
"""

from flask import Blueprint, jsonify, request

from app.services.user_service import UserService

# Create blueprint
user_bp = Blueprint("user", __name__, url_prefix="/api/v1/users")

# Initialize user service
user_service = UserService()


# ==================== USER ROUTES ====================


@user_bp.route("/sync", methods=["POST"])
def sync_user():
    """
    Get or Create User.
    Syncs user from NextAuth to backend database.
    Called by NextAuth after successful Google OAuth.

    Request body:
        {
            "id": "google_user_id",
            "email": "user@example.com",
            "name": "John Doe",
            "profile_picture": "https://..."
        }
    """
    try:
        data = request.get_json()

        user_id = data.get("id")
        email = data.get("email")
        name = data.get("name")
        profile_picture = data.get("profile_picture")

        if not user_id or not email:
            return (
                jsonify({"success": False, "error": "User ID and email are required"}),
                400,
            )

        # Get or create user in backend
        user = user_service.get_or_create_user(
            {
                "id": user_id,
                "email": email,
                "name": name,
                "profile_picture": profile_picture,
            }
        )

        return jsonify({"success": True, "data": user})

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Failed to sync user: {str(e)}"}),
            500,
        )


@user_bp.route("/<user_id>", methods=["GET"])
def get_user(user_id):
    """Get user information by ID."""
    try:
        user = user_service.get_user_by_id(user_id)

        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        return jsonify({"success": True, "data": user})

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Failed to get user: {str(e)}"}),
            500,
        )


@user_bp.route("/<user_id>", methods=["PATCH", "PUT"])
def update_user(user_id):
    """
    Update user profile.
    Handles both general profile updates and onboarding completion.

    Request body can include:
        - username (checked for uniqueness)
        - onboarding_completed (boolean)
        - name, state, city, age_group, pincode
        - political_ideology
    """
    try:
        data = request.get_json()

        # Validate username if provided
        username = data.get("username")
        if username:
            # Check if username is already taken by another user
            is_available = user_service.check_username_available(
                username, exclude_user_id=user_id
            )
            if not is_available:
                return (
                    jsonify({"success": False, "error": "Username is already taken"}),
                    400,
                )

        # Prepare update data
        update_data = {}
        allowed_fields = [
            "name",
            "state",
            "city",
            "age_group",
            "pincode",
            "profile_picture",
            "username",
            "political_ideology",
            "onboarding_completed",
        ]

        for key, value in data.items():
            if key in allowed_fields:
                update_data[key] = value

        # Update user
        updated_user = user_service.update_user_profile(user_id, **update_data)

        if not updated_user:
            return jsonify({"success": False, "error": "User not found"}), 404

        return jsonify(
            {
                "success": True,
                "data": updated_user,
                "message": "User updated successfully",
            }
        )

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Failed to update user: {str(e)}"}),
            500,
        )


@user_bp.route("/check-username", methods=["POST"])
def check_username():
    """
    Check if a username is available.

    Request body:
        {
            "username": "johndoe",
            "user_id": "optional_user_id_to_exclude"
        }
    """
    try:
        data = request.get_json()
        username = data.get("username", "").strip()
        user_id = data.get("user_id")  # Optional: exclude this user from check

        if not username:
            return jsonify({"success": False, "error": "Username is required"}), 400

        # Check if username is available
        is_available = user_service.check_username_available(
            username, exclude_user_id=user_id
        )

        return jsonify({"success": True, "available": is_available})

    except Exception as e:
        return (
            jsonify({"success": False, "error": f"Failed to check username: {str(e)}"}),
            500,
        )


# ==================== HEALTH CHECK ====================


@user_bp.route("/health", methods=["GET"])
def user_health():
    """Check user service health."""
    return jsonify(
        {
            "success": True,
            "service": "User Service",
            "message": "User service is operational",
        }
    )
