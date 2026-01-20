"""
Simple Flask application factory for Rajniti Election Data API.

Clean, minimal setup without unnecessary complexity.
Election data is served directly from JSON files.
Only User table is stored in the database.
"""
import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

from app.core.database import init_db
from app.core.exceptions import RajnitiError
from app.core.response import error_response

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Simple configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["JSON_SORT_KEYS"] = False

    # Enable CORS
    CORS(app)

    # Initialize database for User table only (optional - won't fail if not configured)
    db_initialized = init_db(app)
    if db_initialized:
        logger.info("Database initialized successfully (User table only)")
    else:
        logger.info("Database not initialized - continuing without database")

    # Register routes
    _register_routes(app)

    # Register error handlers
    _register_error_handlers(app)

    return app


def _register_routes(app: Flask) -> None:
    """Register API routes"""
    from app.routes.api_routes import api_bp
    from app.routes.user_routes import user_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(user_bp)


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
