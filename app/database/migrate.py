"""
Automatic database migration runner.

Runs Alembic migrations automatically to keep database in sync with models.
"""
import logging
import os
import time
from pathlib import Path
import traceback

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def _get_retry_settings() -> tuple[int, float]:
    retries_str = os.getenv("DB_MIGRATION_RETRIES", "8")
    delay_str = os.getenv("DB_MIGRATION_DELAY", "2")
    try:
        retries = max(0, int(retries_str))
    except ValueError:
        retries = 8
    try:
        delay = max(0.0, float(delay_str))
    except ValueError:
        delay = 2.0
    return retries, delay


def run_migrations() -> bool:
    """
    Run all pending Alembic migrations.

    Returns:
        bool: True if migrations succeeded, False otherwise
    """
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    alembic_cfg = Config(str(project_root / "alembic.ini"))

    # Set the database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.warning("DATABASE_URL not set. Skipping migrations.")
        return False

    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    retries, delay = _get_retry_settings()
    attempts = retries + 1

    for attempt in range(1, attempts + 1):
        try:
            logger.info(
                "Running database migrations (attempt %s/%s)...",
                attempt,
                attempts,
            )
            command.upgrade(alembic_cfg, "head")
            message = "Database migrations completed successfully"
            logger.info(message)
            print(message)
            return True
        except Exception as e:
            if attempt >= attempts:
                logger.error("Migration failed: %s", e)
                print(f"Migration failed: {e} {traceback.format_exc()}")
                return False
            logger.warning(
                "Migration attempt %s failed: %s. Retrying in %ss...",
                attempt,
                e,
                delay,
            )
            time.sleep(delay)


def sync_db() -> bool:
    """
    Sync database schema with models (auto-generate and run migrations).

    This is a convenience function that:
    1. Auto-generates a migration from model changes
    2. Runs the migration

    Returns:
        bool: True if sync succeeded, False otherwise
    """
    try:
        project_root = Path(__file__).parent.parent.parent
        alembic_cfg = Config(str(project_root / "alembic.ini"))

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.warning("DATABASE_URL not set. Skipping DB sync.")
            return False

        alembic_cfg.set_main_option("sqlalchemy.url", database_url)

        # Auto-generate migration (may create empty migration if no changes)
        logger.info("Auto-generating migration from model changes...")
        message = "Auto-sync: model changes"
        try:
            command.revision(alembic_cfg, autogenerate=True, message=message)
        except Exception as e:
            # If autogenerate fails (e.g., no changes detected), that's okay
            # Just proceed to run existing migrations
            if "Target database is not up to date" in str(e):
                logger.warning(
                    "Database not up to date. Running existing migrations..."
                )
            else:
                logger.debug(f"Autogenerate note: {e}")

        # Run migrations
        logger.info("Running migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("✓ Database sync completed successfully")
        return True

    except Exception as e:
        logger.error(f"✗ Database sync failed: {e}")
        return False
