"""Rajniti backend application factory.

A Flask modular monolith. Modules (`promises`, `reps`, `rag`, `agents`) expose
public facades that are wired here. Boundaries between them are enforced by
`import-linter` (see pyproject.toml).
"""

from __future__ import annotations

from flask import Flask

from app.core.config import Settings


def create_app(settings: Settings | None = None) -> Flask:
    """Build and configure the Flask app.

    Args:
        settings: Optional pre-built settings (useful for tests). Falls back to
            environment-derived settings.
    """
    app = Flask(__name__)
    app.config["SETTINGS"] = settings or Settings.from_env()

    _register_health(app)
    _register_api_v1(app)

    return app


def _register_health(app: Flask) -> None:
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}


def _register_api_v1(app: Flask) -> None:
    from app.api_v1 import api_v1

    app.register_blueprint(api_v1, url_prefix="/api/v1")
