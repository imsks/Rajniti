"""
Database configuration module.

Supports both local PostgreSQL and Supabase (PostgreSQL-based).
"""

import os


def get_database_url() -> str:
    """
    Get database URL from environment variable.

    Set DATABASE_URL to your PostgreSQL connection string.
    Works with both local PostgreSQL and Supabase.

    Environment variable:
    - DATABASE_URL: Full database connection string (required)

    Returns:
        Database URL string compatible with SQLAlchemy

    Raises:
        ValueError: If DATABASE_URL is not set

    Examples:
        Local: postgresql://user:password@localhost:5432/rajniti
        Supabase: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable is required. "
            "Set it to your PostgreSQL connection string (local or Supabase)."
        )
    return database_url


def get_echo_mode() -> bool:
    """
    Get SQLAlchemy echo mode from environment.

    Returns:
        True if SQL queries should be logged, False otherwise
    """
    return os.getenv("DB_ECHO", "false").lower() == "true"
