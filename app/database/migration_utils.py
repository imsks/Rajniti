"""
Idempotent migration utilities.

Provides helper functions to make migrations safe to run multiple times.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    connection = op.get_bind()
    inspector = inspect(connection)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    connection = op.get_bind()
    inspector = inspect(connection)
    return table_name in inspector.get_table_names()


def index_exists(index_name: str) -> bool:
    """Check if an index exists."""
    connection = op.get_bind()
    result = connection.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE indexname = :index_name
            )
        """
        ),
        {"index_name": index_name},
    ).scalar()
    return result


def enum_exists(enum_name: str) -> bool:
    """Check if a PostgreSQL enum type exists."""
    connection = op.get_bind()
    result = connection.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = :enum_name
            )
        """
        ),
        {"enum_name": enum_name},
    ).scalar()
    return result


def safe_add_column(
    table_name: str,
    column_name: str,
    column_type,
    nullable: bool = True,
    **kwargs,
) -> bool:
    """
    Safely add a column to a table (only if it doesn't exist).
    
    Returns:
        bool: True if column was added, False if it already existed
    """
    if column_exists(table_name, column_name):
        return False
    
    op.add_column(table_name, sa.Column(column_name, column_type, nullable=nullable, **kwargs))
    return True


def safe_drop_column(table_name: str, column_name: str) -> bool:
    """
    Safely drop a column from a table (only if it exists).
    
    Returns:
        bool: True if column was dropped, False if it didn't exist
    """
    if not column_exists(table_name, column_name):
        return False
    
    op.drop_column(table_name, column_name)
    return True


def safe_create_table(table_name: str, *columns, **kwargs) -> bool:
    """
    Safely create a table (only if it doesn't exist).
    
    Returns:
        bool: True if table was created, False if it already existed
    """
    if table_exists(table_name):
        return False
    
    op.create_table(table_name, *columns, **kwargs)
    return True


def safe_create_index(index_name: str, table_name: str, columns: list, unique: bool = False) -> bool:
    """
    Safely create an index (only if it doesn't exist).
    
    Returns:
        bool: True if index was created, False if it already existed
    """
    if index_exists(index_name):
        return False
    
    op.create_index(index_name, table_name, columns, unique=unique)
    return True


def safe_create_enum(enum_name: str, values: list) -> bool:
    """
    Safely create a PostgreSQL enum type (only if it doesn't exist).
    
    Returns:
        bool: True if enum was created, False if it already existed
    """
    if enum_exists(enum_name):
        return False
    
    values_str = ", ".join(f"'{v}'" for v in values)
    op.execute(f"CREATE TYPE {enum_name} AS ENUM ({values_str})")
    return True

