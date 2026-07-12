"""Application settings, derived from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for the backend."""

    flask_env: str = "development"
    secret_key: str = "change-me-in-production"
    database_url: str | None = None
    chroma_index_path: str = "/app/index"

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            flask_env=os.getenv("FLASK_ENV", "development"),
            secret_key=os.getenv("SECRET_KEY", "change-me-in-production"),
            database_url=os.getenv("DATABASE_URL"),
            chroma_index_path=os.getenv("CHROMA_INDEX_PATH", "/app/index"),
        )

    @property
    def is_production(self) -> bool:
        return self.flask_env == "production"
