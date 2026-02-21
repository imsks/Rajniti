"""
Database configuration module.

Supports both local PostgreSQL and Supabase (PostgreSQL-based).
"""

import os
import socket
from urllib.parse import urlparse, urlunparse


def _is_running_in_docker() -> bool:
    return os.path.exists("/.dockerenv")


def _maybe_fix_docker_hostname(database_url: str) -> str:
    """
    If running locally (not in Docker) and the URL points to host "postgres",
    swap to localhost to avoid DNS errors.
    """
    try:
        parsed = urlparse(database_url)
    except Exception:
        return database_url

    if parsed.hostname != "postgres":
        return database_url

    if _is_running_in_docker():
        return database_url

    # If "postgres" doesn't resolve locally, fallback to localhost.
    try:
        socket.getaddrinfo(parsed.hostname, parsed.port or 5432)
        return database_url
    except socket.gaierror:
        pass

    netloc = parsed.netloc.replace("postgres", "localhost", 1)
    return urlunparse(parsed._replace(netloc=netloc))


def get_database_url(required: bool = False) -> str:
    """
    Get database URL from environment variable.

    Set DATABASE_URL to your PostgreSQL connection string.
    Works with both local PostgreSQL and Supabase.

    Environment variable:
    - DATABASE_URL: Full database connection string (required)

    Args:
        required: If True, raise ValueError when DATABASE_URL is missing.

    Returns:
        Database URL string compatible with SQLAlchemy.
        If `required=False` and DATABASE_URL is missing, returns an empty string.

    Examples:
        Local: postgresql://user:password@localhost:5432/rajniti
        Supabase: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        if required:
            raise ValueError(
                "DATABASE_URL environment variable is required. "
                "Set it to your PostgreSQL connection string (local or Supabase)."
            )
        return ""
    return _maybe_fix_docker_hostname(database_url)


def get_echo_mode() -> bool:
    """
    Get SQLAlchemy echo mode from environment.

    Returns:
        True if SQL queries should be logged, False otherwise
    """
    return os.getenv("DB_ECHO", "false").lower() == "true"
