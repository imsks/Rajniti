"""add phone preferred_parties topics_of_interest

Revision ID: 3b442eec1811
Revises: 44a45c594b37
Create Date: 2026-04-01 12:50:55.221640

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "3b442eec1811"
down_revision: Union[str, None] = "44a45c594b37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(), nullable=True))
    op.add_column("users", sa.Column("preferred_parties", sa.JSON(), nullable=True))
    op.add_column("users", sa.Column("topics_of_interest", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "topics_of_interest")
    op.drop_column("users", "preferred_parties")
    op.drop_column("users", "phone")
