#!/usr/bin/env python3
"""
Database CLI: alembic upgrade and ORM init.

Usage:
  python scripts/db.py migrate          # alembic upgrade head
  python scripts/db.py init             # SQLAlchemy create_all (no Alembic)
  python scripts/db.py autogenerate -m "description"  # generate migration
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv

load_dotenv(REPO_ROOT / ".env")


def upgrade_head() -> None:
    """Run alembic upgrade head."""
    if not (os.getenv("DATABASE_URL") or "").strip():
        raise RuntimeError("DATABASE_URL is not set.")

    from alembic import command
    from alembic.config import Config

    prev = os.getcwd()
    try:
        os.chdir(REPO_ROOT)
        cfg = Config(str(REPO_ROOT / "alembic.ini"))
        command.upgrade(cfg, "head")
    finally:
        os.chdir(prev)


def init_tables() -> None:
    """Create tables from SQLAlchemy models (no Alembic)."""
    from app.database.session import init_db

    init_db()


def autogenerate(message: str) -> None:
    """Run alembic revision --autogenerate."""
    if not (os.getenv("DATABASE_URL") or "").strip():
        raise RuntimeError("DATABASE_URL is not set.")

    from alembic import command
    from alembic.config import Config

    prev = os.getcwd()
    try:
        os.chdir(REPO_ROOT)
        cfg = Config(str(REPO_ROOT / "alembic.ini"))
        command.revision(cfg, message=message, autogenerate=True)
    finally:
        os.chdir(prev)


def main() -> None:
    parser = argparse.ArgumentParser(description="Rajniti database")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("migrate", help="Run alembic upgrade head")
    sub.add_parser("init", help="Create tables via SQLAlchemy metadata.create_all")
    auto = sub.add_parser("autogenerate", help="Generate migration from model diff")
    auto.add_argument("-m", "--message", required=True, help="Migration description")

    args = parser.parse_args()
    if args.cmd == "migrate":
        upgrade_head()
        print("OK: alembic upgrade head")
    elif args.cmd == "init":
        init_tables()
        print("OK: tables ensured via create_all")
    elif args.cmd == "autogenerate":
        autogenerate(args.message)
        print(
            "OK: migration generated — review alembic/versions/ before running migrate"
        )


if __name__ == "__main__":
    main()
