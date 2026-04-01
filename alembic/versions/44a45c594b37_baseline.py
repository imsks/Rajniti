"""Baseline: matches the users table already in production.

Revision ID: 44a45c594b37
Revises:
Create Date: 2026-03-31

This is a no-op migration. It exists so Alembic's revision chain
matches the alembic_version row already stamped in the database.
"""

from typing import Sequence, Union

revision: str = "44a45c594b37"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
