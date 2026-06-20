"""
Flask application factory for Rajniti API.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

from app.core.exceptions import RajnitiError  # noqa: E402
from app.core.response import error_response  # noqa: E402

logger = logging.getLogger(__name__)


def _auto_migrate() -> None:
    """Run alembic upgrade head via scripts/db.py (loaded dynamically)."""
    import importlib.util
    import sys

    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    path = root / "scripts" / "db.py"
    spec = importlib.util.spec_from_file_location("rajniti_scripts_db", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.upgrade_head()


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
        logger.debug("TESTING=true: skipping auto-migrate and create_all.")
        return

    if os.getenv("SKIP_DB_AUTO_MIGRATE", "").lower() not in ("1", "true", "yes"):
        try:
            _auto_migrate()
            logger.info("Database migrations applied (alembic upgrade head).")
        except Exception as exc:
            logger.exception(
                "Auto-migrate failed (set SKIP_DB_AUTO_MIGRATE=1 to disable): %s",
                exc,
            )

    if os.getenv("SKIP_DB_AUTO_CREATE", "").lower() in ("1", "true", "yes"):
        logger.info("SKIP_DB_AUTO_CREATE is set; skipping create_all.")
        return

    try:
        from app.database.session import init_db as ensure_db_schema

        ensure_db_schema()
        logger.info("Database tables ensured (SQLAlchemy metadata.create_all).")
    except Exception as exc:
        logger.exception(
            "Failed to apply ORM schema: %s. "
            "Local: check DATABASE_URL matches Postgres in compose. "
            "Supabase: use session-mode pooler (port 5432). "
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
    from app.routes.scrape_routes import scrape_bp
    from app.routes.user_routes import user_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(scrape_bp)
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
