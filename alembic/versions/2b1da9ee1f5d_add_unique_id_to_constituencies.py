"""add_unique_id_to_constituencies

Revision ID: 2b1da9ee1f5d
Revises: 
Create Date: 2025-11-13 13:42:04.451441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.database.migration_utils import column_exists, safe_add_column


# revision identifiers, used by Alembic.
revision: str = '2b1da9ee1f5d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add original_id columns - idempotent migration."""
    connection = op.get_bind()
    
    # Step 1: Add columns as nullable first (to handle existing data) - idempotent
    safe_add_column('candidates', 'original_constituency_id', sa.String(), nullable=True)
    safe_add_column('constituencies', 'original_id', sa.String(), nullable=True)
    
    # Step 2: Populate original_id from existing id values in constituencies
    # This preserves the original ID before we potentially change the id column
    if column_exists('constituencies', 'original_id'):
        op.execute("""
            UPDATE constituencies 
            SET original_id = id 
            WHERE original_id IS NULL
        """)
    
    # Step 3: Populate original_constituency_id from existing constituency_id in candidates
    if column_exists('candidates', 'original_constituency_id'):
        op.execute("""
            UPDATE candidates 
            SET original_constituency_id = constituency_id 
            WHERE original_constituency_id IS NULL
        """)
    
    # Step 4: Make original_id NOT NULL now that it's populated (only if column exists)
    if column_exists('constituencies', 'original_id'):
        # Check current nullable status
        from sqlalchemy import inspect
        inspector = inspect(connection)
        columns = {col['name']: col for col in inspector.get_columns('constituencies')}
        if 'original_id' in columns and columns['original_id']['nullable']:
            op.alter_column('constituencies', 'original_id', nullable=False)


def downgrade() -> None:
    """Remove original_id columns - idempotent."""
    from app.database.migration_utils import safe_drop_column
    
    safe_drop_column('constituencies', 'original_id')
    safe_drop_column('candidates', 'original_constituency_id')
