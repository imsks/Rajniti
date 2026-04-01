"""
Database configuration module.

Supports local PostgreSQL, Docker Postgres, and Supabase.
"""

import logging
import os
import socket
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)


def _is_running_in_docker() -> bool:
    return os.path.exists("/.dockerenv")


def _maybe_fix_docker_hostname(database_url: str) -> str:
    """
    When running on the host (not in Docker) and URL has host="postgres",
    swap to localhost so venv dev works against Docker-published port.
    """
    try:
        parsed = urlparse(database_url)
    except Exception:
        return database_url

    if parsed.hostname != "postgres":
        return database_url

    if _is_running_in_docker():
        return database_url

    try:
        socket.getaddrinfo(parsed.hostname, parsed.port or 5432)
        return database_url
    except socket.gaierror:
        pass

    netloc = parsed.netloc.replace("postgres", "localhost", 1)
    return urlunparse(parsed._replace(netloc=netloc))


def get_database_url(required: bool = False) -> str:
    """Return DATABASE_URL from env, with Docker hostname fixup."""
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        if required:
            raise ValueError(
                "DATABASE_URL environment variable is required. "
                "Set it to your PostgreSQL connection string."
            )
        return ""
    return _maybe_fix_docker_hostname(database_url)


def get_echo_mode() -> bool:
    return os.getenv("DB_ECHO", "false").lower() == "true"


def _is_postgres_url(database_url: str) -> bool:
    try:
        scheme = (urlparse(database_url).scheme or "").split("+")[0].lower()
        return scheme in ("postgresql", "postgres")
    except Exception:
        return False


def resolve_ipv4(host: str, port: int) -> str:
    """Resolve host to an IPv4 address. Returns empty string on failure."""
    try:
        infos = socket.getaddrinfo(
            host, port,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
        if infos:
            return infos[0][4][0]
    except socket.gaierror:
        pass

    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return ""


def get_connect_args() -> dict:
    """
    Build psycopg2 connect_args dict.

    For Postgres URLs: forces IPv4 via hostaddr to avoid Docker IPv6 failures.
    For non-Postgres URLs (e.g. sqlite): returns empty dict.

    Disable with DATABASE_SKIP_IPV4_FORCE=1.
    Override with DATABASE_HOSTADDR=<ip>.
    """
    if os.getenv("DATABASE_SKIP_IPV4_FORCE", "").lower() in ("1", "true", "yes"):
        return {}

    database_url = get_database_url()
    if not database_url or not _is_postgres_url(database_url):
        return {}

    try:
        parsed = urlparse(database_url)
    except Exception:
        return {}

    host = parsed.hostname
    if not host:
        return {}

    manual = os.getenv("DATABASE_HOSTADDR", "").strip()
    if manual:
        logger.info("Using DATABASE_HOSTADDR=%s for host=%s", manual, host)
        return {"hostaddr": manual}

    hostaddr = resolve_ipv4(host, parsed.port or 5432)
    if hostaddr:
        logger.info("Forcing IPv4 hostaddr=%s for host=%s", hostaddr, host)
        return {"hostaddr": hostaddr}

    logger.warning(
        "Could not resolve IPv4 for host %r. "
        "This host is likely IPv6-only and WILL FAIL in Docker. "
        "For Supabase, use the session-mode pooler URL "
        "(aws-0-REGION.pooler.supabase.com:5432) instead of the direct URL.",
        host,
    )
    return {}


def is_transaction_pooler(database_url: str) -> bool:
    """True when URL looks like Supabase/PgBouncer transaction pooler (port 6543)."""
    if not database_url:
        return False
    try:
        parsed = urlparse(database_url)
    except Exception:
        return False
    return parsed.port == 6543 or "pooler" in (parsed.hostname or "").lower()
