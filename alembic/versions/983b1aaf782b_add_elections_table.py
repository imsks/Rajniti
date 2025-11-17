"""add_elections_table

Revision ID: 983b1aaf782b
Revises: 2b1da9ee1f5d
Create Date: 2025-11-13 19:05:32.299004

"""
import json
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.database.migration_utils import (
    enum_exists,
    table_exists,
    index_exists,
    safe_create_enum,
    safe_create_index,
)


# revision identifiers, used by Alembic.
revision: str = '983b1aaf782b'
down_revision: Union[str, None] = '2b1da9ee1f5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create elections table - idempotent migration."""
    connection = op.get_bind()
    
    # Check and create enum types if they don't exist - idempotent
    safe_create_enum('election_type', ['LOK_SABHA', 'VIDHAN_SABHA'])
    safe_create_enum('result_status', ['DECLARED', 'PENDING', 'ONGOING'])
    
    # Check if elections table already exists
    if table_exists('elections'):
        # Table already exists, skip creation but ensure data is inserted
        print("Elections table already exists, skipping table creation")
    else:
        # Create elections table
        op.create_table(
        'elections',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('LOK_SABHA', 'VIDHAN_SABHA', name='election_type', create_type=False), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('total_constituencies', sa.Integer(), nullable=True),
        sa.Column('total_candidates', sa.Integer(), nullable=True),
        sa.Column('total_parties', sa.Integer(), nullable=True),
        sa.Column('result_status', sa.Enum('DECLARED', 'PENDING', 'ONGOING', name='result_status', create_type=False), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes - idempotent
        safe_create_index('ix_elections_year', 'elections', ['year'], unique=False)
        safe_create_index('ix_elections_id', 'elections', ['id'], unique=False)
    
    # Load and insert election data from JSON (if file exists)
    data_path = Path('app/data/elections/LS-2024.json')
    
    if data_path.exists():
        with open(data_path, 'r', encoding='utf-8') as f:
            elections_data = json.load(f)
        
        for election in elections_data:
            # Convert date string to date object if present
            election_date = None
            if election.get('date'):
                from datetime import datetime
                election_date = datetime.strptime(election['date'], '%Y-%m-%d').date()
            
            connection.execute(
                sa.text("""
                    INSERT INTO elections (
                        id, name, type, year, date,
                        total_constituencies, total_candidates, total_parties,
                        result_status
                    ) VALUES (
                        :id, :name, :type, :year, :date,
                        :total_constituencies, :total_candidates, :total_parties,
                        :result_status
                    )
                """),
                {
                    'id': election['election_id'],
                    'name': election['name'],
                    'type': election['type'],
                    'year': election['year'],
                    'date': election_date,
                    'total_constituencies': election.get('total_constituencies'),
                    'total_candidates': election.get('total_candidates'),
                    'total_parties': election.get('total_parties'),
                    'result_status': election.get('result_status'),
                }
            )
    else:
        # If JSON file doesn't exist, insert default Lok Sabha 2024 election
        # Check if election already exists before inserting
        existing = connection.execute(
            sa.text("SELECT id FROM elections WHERE id = :id"),
            {"id": "lok-sabha-2024"}
        ).first()
        
        if not existing:
            connection.execute(
                sa.text("""
                    INSERT INTO elections (
                        id, name, type, year, date,
                        total_constituencies, total_candidates, total_parties,
                        result_status
                    ) VALUES (
                        'lok-sabha-2024', 'Lok Sabha General Election 2024', 'LOK_SABHA', 2024, NULL,
                        543, 8902, 42,
                        'DECLARED'
                    )
                """)
            )


def downgrade() -> None:
    """Drop elections table - idempotent."""
    from app.database.migration_utils import index_exists, table_exists
    
    # Drop indexes - idempotent
    if index_exists('ix_elections_id'):
        op.drop_index(op.f('ix_elections_id'), table_name='elections')
    if index_exists('ix_elections_year'):
        op.drop_index(op.f('ix_elections_year'), table_name='elections')
    
    # Drop elections table - idempotent
    if table_exists('elections'):
        op.drop_table('elections')
    
    # Drop enum types - idempotent
    if enum_exists('election_type'):
        op.execute("DROP TYPE election_type")
    if enum_exists('result_status'):
        op.execute("DROP TYPE result_status")
