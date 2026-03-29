"""
User routes for user data management.
"""

from flask import Blueprint, jsonify, request

# Create blueprint
user_bp = Blueprint("user", __name__, url_prefix="/api/v1/users")

# ❌ REMOVE this (causes freeze)
# from app.services.user_service import UserService
# user_service = UserService()

# ✅ LAZY LOAD (FIX)
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
    try:
        data = request.get_json()

        user_id = data.get("id")
        email = data.get("email")
        name = data.get("name")

        print("🔥 SAVING USER:", data)

        # ✅ SIMPLE SQLITE SAVE
        import sqlite3

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT,
                name TEXT
            )
        """)

        cursor.execute("""
            INSERT OR REPLACE INTO users (id, email, name)
            VALUES (?, ?, ?)
        """, (user_id, email, name))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "data": {
                "id": user_id,
                "email": email,
                "name": name
            }
        }

    except Exception as e:
        return {"success": False, "error": str(e)}, 500


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

        update_data = {}
        allowed_fields = [
            "name", "state", "city", "age_group", "pincode",
            "profile_picture", "username", "political_ideology",
            "onboarding_completed",
        ]

        for key, value in data.items():
            if key in allowed_fields:
                update_data[key] = value

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
        user_id = data.get("user_id")

        if not username:
            return jsonify({"success": False, "error": "Username is required"}), 400

        is_available = get_user_service().check_username_available(
            username, exclude_user_id=user_id
        )

        return jsonify({"success": True, "available": is_available})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



@user_bp.route("/all", methods=["GET"])
def get_all_users():
    import sqlite3

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    conn.close()

    return {
        "success": True,
        "users": users
    }        


# ==================== HEALTH CHECK ====================

@user_bp.route("/health", methods=["GET"])
def user_health():
    return jsonify({
        "success": True,
        "service": "User Service",
        "message": "User service is operational",
    })