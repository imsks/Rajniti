# Database Layer Documentation

This directory contains the database layer for Rajniti Election Data API.

## Overview

The database layer provides:

-   **DB Models** with CRUD operations for Party, Constituency, and Candidate
-   **PostgreSQL Support** compatible with both local PostgreSQL and Supabase
-   **Alembic Migrations** for database schema management
-   **JSON to DB Migration** script to migrate existing JSON data

## Structure

```
app/database/
├── __init__.py           # Package exports
├── base.py               # Base model class and utilities
├── config.py             # Database configuration
├── session.py            # Database session management
└── models/               # Database models
    ├── __init__.py
    ├── party.py          # Party model with CRUD
    ├── constituency.py   # Constituency model with CRUD
    └── candidate.py      # Candidate model with CRUD
```

## Database Configuration

Set the `DATABASE_URL` environment variable to your PostgreSQL connection string.

Works with both **local PostgreSQL** and **Supabase**.

### Local PostgreSQL

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/rajniti"
```

### Supabase

```bash
export DATABASE_URL="postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres"
```

**Note:** Get your Supabase connection string from: Project Settings → Database → Connection String (URI format)

## Setup

### 1. Local PostgreSQL Setup

```bash
# Install PostgreSQL (if not already installed)
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS (with Homebrew)
brew install postgresql

# Start PostgreSQL
sudo service postgresql start  # Linux
brew services start postgresql  # macOS

# Create database
createdb rajniti

# Or using psql
psql -U postgres
CREATE DATABASE rajniti;
\q
```

If Above doesn't work, You may not have your user created. Follow the steps below -

1. Connect via Default User

```
psql -d postgres
```

2. Check existing roles

```
\du
```

3. Create a New User with Password. Remember the password as You'll need for DB Connection

```
CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres';
```

4. Log in via newly created user

```
psql -U postgres -d postgres
```

5. Create DB

```
CREATE DATABASE rajniti;
```

### 2. Supabase Setup

1. Create a Supabase project at https://supabase.com
2. Get your database connection string from:
    - Project Settings → Database → Connection String
    - Use the "URI" format (pooler connection recommended)
3. Set the `DATABASE_URL` environment variable

### 3. Initialize Database

```bash
# Activate virtual environment
source venv/bin/activate

# Set database URL (local or Supabase)
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/rajniti"
# OR for Supabase:
# export DATABASE_URL="postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres"

# Initialize database (creates tables)
python -c "from app.database import init_db; init_db()"
```

## Database Migrations

**Simple & Automatic**: Migrations run automatically when the server starts. Just update your models and run the server or sync script.

### Automatic Migrations

Migrations are **idempotent** (safe to run multiple times) and run automatically:

1. **On Server Start**: Migrations run automatically when you start the server
2. **Manual Sync**: Run `python scripts/db.py sync` to sync models to database

### Workflow

**That's it!** Just update your models and:

```bash
# Option 1: Start the server (migrations run automatically)
python run.py

# Option 2: Manually sync (if you want to update DB without starting server)
python scripts/db.py sync
```

### Migration Features

-   ✅ **Idempotent**: Safe to run multiple times - won't fail if columns/tables already exist
-   ✅ **Automatic**: Runs on server startup
-   ✅ **Simple**: No manual migration steps needed

### Manual Migration Commands (Advanced)

If you need manual control:

```bash
# Apply all pending migrations
alembic upgrade head

# View current migration status
alembic current

# View migration history
alembic history
```

## Migrating JSON Data to Database

A migration script is provided to import existing JSON data into the database.

### Basic Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Set database URL
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/rajniti"

# Run migration (default: Lok Sabha 2024 data)
python scripts/migrations/migrate_json_to_db.py
```

### Advanced Usage

```bash
# Dry run (see what would be done without making changes)
python scripts/migrations/migrate_json_to_db.py --dry-run

# Migrate specific election data
python scripts/migrations/migrate_json_to_db.py --election-dir app/data/lok_sabha/lok-sabha-2024

# Migrate Vidhan Sabha data (if available)
python scripts/migrations/migrate_json_to_db.py --election-dir app/data/vidhan_sabha/DL_2025_ASSEMBLY
```

## Using Database Models

### Party Model

```python
from app.database import get_db_session
from app.database.models import Party

# Create a party
with get_db_session() as session:
    party = Party.create(
        session=session,
        id="123",
        name="Example Party",
        short_name="EP",
        symbol="Lotus"
    )

# Get party by ID
with get_db_session() as session:
    party = Party.get_by_id(session, "123")
    print(party.name)

# Get all parties
with get_db_session() as session:
    parties = Party.get_all(session, skip=0, limit=100)

# Update party
with get_db_session() as session:
    party = Party.get_by_id(session, "123")
    party.update(session, symbol="Elephant")

# Delete party
with get_db_session() as session:
    party = Party.get_by_id(session, "123")
    party.delete(session)
```

### Constituency Model

```python
from app.database import get_db_session
from app.database.models import Constituency

# Create a constituency
with get_db_session() as session:
    const = Constituency.create(
        session=session,
        id="1",
        name="New Delhi",
        state_id="DL"
    )

# Get constituency by state
with get_db_session() as session:
    constituencies = Constituency.get_by_state(session, "DL")
```

### Candidate Model

```python
from app.database import get_db_session
from app.database.models import Candidate

# Create a candidate
with get_db_session() as session:
    candidate = Candidate.create(
        session=session,
        id="abc-123",
        name="John Doe",
        party_id="123",
        constituency_id="1",
        state_id="DL",
        status="WON",
        type="MP",
        image_url="https://example.com/photo.jpg"
    )

# Search candidates by name
with get_db_session() as session:
    candidates = Candidate.search_by_name(session, "John")

# Get winners
with get_db_session() as session:
    winners = Candidate.get_winners(session, skip=0, limit=100)

# Get candidates by party
with get_db_session() as session:
    candidates = Candidate.get_by_party(session, "123")
```

## Bulk Operations

All models support bulk creation for efficient data loading:

```python
from app.database import get_db_session
from app.database.models import Party, Constituency, Candidate

# Bulk create parties
parties_data = [
    {"id": "1", "name": "Party A", "short_name": "PA", "symbol": ""},
    {"id": "2", "name": "Party B", "short_name": "PB", "symbol": ""},
]

with get_db_session() as session:
    Party.bulk_create(session, parties_data)
```

## Database Service Layer (Future Enhancement)

To integrate the database with the existing API, you can create a database service:

```python
# app/services/db_data_service.py
from app.database import get_db_session
from app.database.models import Party, Constituency, Candidate
from app.services.data_service import DataService

class DbDataService(DataService):
    """Database-backed data service implementation."""

    def get_parties(self, election_id: str):
        with get_db_session() as session:
            return Party.get_all(session)

    # Implement other DataService methods...
```

## Quick Reference: Database Operations

### Common psql Commands

```bash
# Connect to database
psql "postgresql://user:password@host:port/database"
psql -U username -d database_name

# List all databases
\l

# Connect to a specific database
\c database_name

# List all tables
\dt

# Describe a table structure
\d table_name
\d+ table_name  # More detailed

# List all columns in a table
\d+ table_name

# Show table size
\dt+ table_name

# List all schemas
\dn

# Show current database
SELECT current_database();

# Show current user
SELECT current_user;

# Exit psql
\q
```

### Common SQL Queries

```sql
-- Count rows in a table
SELECT COUNT(*) FROM table_name;

-- View all data (limit results)
SELECT * FROM table_name LIMIT 10;

-- View specific columns
SELECT column1, column2 FROM table_name;

-- Filter data
SELECT * FROM table_name WHERE column_name = 'value';

-- Sort results
SELECT * FROM table_name ORDER BY column_name DESC;

-- Group and aggregate
SELECT state_id, COUNT(*)
FROM constituencies
GROUP BY state_id;

-- Join tables
SELECT c.name, p.name as party_name
FROM candidates c
JOIN parties p ON c.party_id = p.id
LIMIT 10;
```

### Check Database Connection

```bash
# Test connection from command line
psql $DATABASE_URL -c "SELECT version();"

# Test using Python
python -c "from app.database.config import get_database_url; print(get_database_url())"
```

## Troubleshooting

### Connection Issues

```bash
# Test database connection
python -c "from app.database.config import get_database_url; print(get_database_url())"

# Test with psql
psql "postgresql://postgres:postgres@localhost:5432/rajniti"
```

### Migration Issues

```bash
# Reset database (WARNING: deletes all data)
alembic downgrade base
alembic upgrade head

# Or drop and recreate
dropdb rajniti
createdb rajniti
python -c "from app.database import init_db; init_db()"
```

### Permission Issues

```bash
# Grant permissions to user
psql -U postgres
GRANT ALL PRIVILEGES ON DATABASE rajniti TO your_user;
\q
```

## Environment Variables Reference

| Variable       | Description                           | Example                                                   |
| -------------- | ------------------------------------- | --------------------------------------------------------- |
| `DATABASE_URL` | Database connection string (required) | `postgresql://user:pass@host:5432/db` (local or Supabase) |
| `DB_ECHO`      | Log SQL queries                       | `true` or `false`                                         |

## Security Considerations

1. **Never commit database credentials** to version control
2. Use **environment variables** for all sensitive data
3. For production, use **strong passwords** and **SSL connections**
4. For Supabase, enable **Row Level Security (RLS)** policies
5. Regularly **backup your database**

## Performance Tips

1. Use **bulk operations** for large data imports
2. Add **indexes** on frequently queried columns (already done for key fields)
3. Use **connection pooling** (already configured in session.py)
4. For large datasets, use **pagination** with skip/limit parameters
5. Consider **caching** frequently accessed data
