"""add onboarded_from and Saransh fields to users

`users` is shared with Saransh, which keeps everything it asks a User here
instead of in its own table. Every column is additive and safe for the live
app: `onboarded_from` defaults to 'rajniti' on the server, so existing rows are
backfilled and inserts from code that predates this column stay correct.

Revision ID: c4d5e6f7a8b9
Revises: 9b6f4d1c2a10
Create Date: 2026-11-12

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, None] = "9b6f4d1c2a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "onboarded_from",
            sa.String(),
            nullable=False,
            server_default="rajniti",
        ),
    )
    op.add_column("users", sa.Column("saransh_topics", sa.JSON(), nullable=True))
    op.add_column("users", sa.Column("saransh_interests", sa.JSON(), nullable=True))
    op.add_column(
        "users", sa.Column("saransh_onboarded_at", sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("users", "saransh_onboarded_at")
    op.drop_column("users", "saransh_interests")
    op.drop_column("users", "saransh_topics")
    op.drop_column("users", "onboarded_from")
