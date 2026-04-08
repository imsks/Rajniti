"""
Alembic migration environment.

Uses create_engine directly to:
1. Avoid ConfigParser %-interpolation bugs with URLs containing encoded chars.
2. Apply get_connect_args() for consistent IPv4 forcing.
"""

from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context
from app.database.base import Base
from app.database.config import get_connect_args, get_database_url
from app.database.models import User  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _require_database_url() -> str:
    url = get_database_url()
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Export it or add it to .env before running migrations."
        )
    return url


def run_migrations_offline() -> None:
    url = _require_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


_TRACKED_TABLES = set(target_metadata.tables)


def _include_name(name, type_, parent_names):
    """Only track tables that belong to our SQLAlchemy models."""
    if type_ == "table":
        return name in _TRACKED_TABLES
    return True


def _include_object(obj, name, type_, reflected, compare_to):
    """Skip FK constraints that reference tables outside our models."""
    if type_ == "foreign_key_constraint" and reflected:
        referred = obj.referred_table.name if obj.referred_table is not None else None
        if referred and referred not in _TRACKED_TABLES:
            return False
    return True


def run_migrations_online() -> None:
    url = _require_database_url()
    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
        connect_args=get_connect_args(),
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_name=_include_name,
            include_object=_include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
