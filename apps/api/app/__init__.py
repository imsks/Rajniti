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
    resolved = settings or Settings.from_env()

    # Flask signs session cookies with SECRET_KEY, so the configured value has
    # to reach app.config under that exact name — stashing it only under
    # "SETTINGS" would leave sessions signed with Flask's insecure default.
    if resolved.is_production and resolved.secret_key == Settings.secret_key:
        raise RuntimeError(
            "SECRET_KEY is still the built-in placeholder while FLASK_ENV=production. "
            "Set a real SECRET_KEY (GCP Secret Manager in prod) before serving traffic."
        )

    app.config["SECRET_KEY"] = resolved.secret_key
    app.config["SETTINGS"] = resolved

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
