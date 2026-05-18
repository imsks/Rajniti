"""add user_politicians table

Revision ID: 9b6f4d1c2a10
Revises: 3b442eec1811
Create Date: 2026-05-18

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "9b6f4d1c2a10"
down_revision: Union[str, None] = "3b442eec1811"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_politicians",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("politician_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id", "role"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_user_politicians_user_id",
        "user_politicians",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_politicians_user_id", table_name="user_politicians")
    op.drop_table("user_politicians")
