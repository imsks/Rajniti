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


def get_psycopg2_connect_args() -> dict:
    """
    Prefer IPv4 via hostaddr when the hostname resolves to A records (helps some
    Docker ↔ cloud Postgres paths). Set DATABASE_SKIP_IPV4_FORCE=1 to disable.
    Only applied for postgresql/postgres URLs (not SQLite).
    """
    if os.getenv("DATABASE_SKIP_IPV4_FORCE", "").lower() in ("1", "true", "yes"):
        return {}

    database_url = get_database_url()
    if not database_url:
        return {}

    try:
        parsed = urlparse(database_url)
    except Exception:
        return {}

    scheme = (parsed.scheme or "").split("+")[0].lower()
    if scheme not in ("postgresql", "postgres"):
        return {}

    host = parsed.hostname
    if not host:
        return {}

    port = parsed.port or 5432
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return {}

    v4 = [info for info in infos if info[0] == socket.AF_INET]
    if not v4:
        return {}

    return {"hostaddr": v4[0][4][0]}


def database_url_looks_like_transaction_pooler(database_url: str) -> bool:
    """Transaction poolers often break DDL (create_all)."""
    if not database_url:
        return False
    try:
        parsed = urlparse(database_url)
    except Exception:
        return False
    host = (parsed.hostname or "").lower()
    port = parsed.port
    return port == 6543 or "pooler" in host
