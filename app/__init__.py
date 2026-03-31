"""
Flask application factory for Rajniti API.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from app.core.exceptions import RajnitiError
from app.core.response import error_response

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger(__name__)


def _configure_database() -> None:
    """Create SQLAlchemy engine when DATABASE_URL is present."""
    url = (os.getenv("DATABASE_URL") or "").strip()
    if not url:
        logger.warning(
            "DATABASE_URL is not set. Database-backed routes (users, health DB) "
            "will not work until you add it to the project root .env. "
            "Docker: ensure compose env_file points at that .env."
        )
        return

    from app.database.session import init_engine

    if init_engine() is None:
        logger.error(
            "DATABASE_URL is set but the SQLAlchemy engine did not start. "
            "Check credentials, sslmode, host name (use 'postgres' for the "
            "local-db compose profile, not localhost from inside the API container)."
        )
        return

    logger.info("SQLAlchemy engine initialized.")

    if os.getenv("TESTING", "").lower() in ("1", "true", "yes"):
        logger.debug("TESTING=true: skipping automatic create_all.")
        return

    if os.getenv("SKIP_DB_AUTO_CREATE", "").lower() in ("1", "true", "yes"):
        logger.info("SKIP_DB_AUTO_CREATE is set; skipping create_all (use Alembic or SQL manually).")
        return

    try:
        from app.database.session import init_db as ensure_db_schema

        ensure_db_schema()
        logger.info("Database tables ensured (SQLAlchemy metadata.create_all).")
    except Exception as exc:
        logger.exception(
            "Failed to apply ORM schema: %s. "
            "Local: check DATABASE_URL matches Postgres in compose. "
            "Supabase: use direct connection (port 5432), not pooler (6543); add ?sslmode=require. "
            "Or set SKIP_DB_AUTO_CREATE=1 and run Alembic.",
            exc,
        )


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["JSON_SORT_KEYS"] = False
    CORS(app)

    _configure_database()

    _register_blueprints(app)
    _register_error_handlers(app)
    return app


def _register_blueprints(app: Flask) -> None:
    from app.routes.api_routes import api_bp
    from app.routes.user_routes import user_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(user_bp)


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(RajnitiError)
    def handle_rajniti_error(error):
        return error_response(error.message, error.code)

    @app.errorhandler(404)
    def handle_not_found(error):
        return error_response("Endpoint not found", 404)

    @app.errorhandler(500)
    def handle_server_error(error):
        return error_response("Internal server error", 500)
