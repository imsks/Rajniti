"""
Simple Flask application factory for Rajniti Election Data API.
"""

import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

from app.core.exceptions import RajnitiError
from app.core.response import error_response

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask application"""

    app = Flask(__name__)

    # Basic config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["JSON_SORT_KEYS"] = False

    # Enable CORS
    CORS(app)

    # ============================================================
    # 🚫 TEMP DISABLED: DB INIT + MIGRATIONS (SAFE MODE)
    # ============================================================

    logger.info("🚫 Skipping DB init and migrations (SAFE MODE)")

    # ============================================================
    # ✅ ROOT ROUTE
    # ============================================================

    @app.route("/")
    def home():
        return {"status": "working"}

    # ============================================================
    # 🚫 TEMP DISABLED: HEAVY ROUTES
    # ============================================================

    
    from app.routes.api_routes import api_bp
    app.register_blueprint(api_bp)
    

    # ============================================================
    # ✅ LOAD USER ROUTES (FIXED POSITION + INDENT)
    # ============================================================

    try:
        print("👉 Loading user_routes...")
        from app.routes.user_routes import user_bp
        app.register_blueprint(user_bp)
        print("✅ user_routes loaded")
    except Exception as e:
        print("❌ ERROR loading user_routes:", e)

    # ============================================================
    # ERROR HANDLERS
    # ============================================================

    _register_error_handlers(app)

    return app


def _register_error_handlers(app: Flask) -> None:
    """Register error handlers"""

    @app.errorhandler(RajnitiError)
    def handle_rajniti_error(error):
        return error_response(error.message, error.code)

    @app.errorhandler(404)
    def handle_not_found(error):
        return error_response("Endpoint not found", 404)

    @app.errorhandler(500)
    def handle_server_error(error):
        return error_response("Internal server error", 500)