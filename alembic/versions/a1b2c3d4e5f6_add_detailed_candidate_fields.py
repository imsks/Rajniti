"""add_detailed_candidate_fields

Revision ID: a1b2c3d4e5f6
Revises: 80101d0839fc
Create Date: 2025-11-13 14:35:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from app.database.migration_utils import column_exists, safe_add_column

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "80101d0839fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add detailed candidate information fields - idempotent migration."""

    # Add education_background column
    safe_add_column("candidates", "education_background", sa.JSON(), nullable=True)

    # Add political_background column
    safe_add_column("candidates", "political_background", sa.JSON(), nullable=True)

    # Add family_background column
    safe_add_column("candidates", "family_background", sa.JSON(), nullable=True)

    # Add assets column
    safe_add_column("candidates", "assets", sa.JSON(), nullable=True)


def downgrade() -> None:
    """Remove detailed candidate information fields - idempotent."""
    from app.database.migration_utils import safe_drop_column

    safe_drop_column("candidates", "assets")
    safe_drop_column("candidates", "family_background")
    safe_drop_column("candidates", "political_background")
    safe_drop_column("candidates", "education_background")
