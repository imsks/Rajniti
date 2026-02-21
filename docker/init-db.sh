#!/bin/bash
# Auto-create user/database from DATABASE_URL
# This runs on first postgres container startup

set -e

if [ -z "$DATABASE_URL" ]; then
    echo "No DATABASE_URL set, using defaults"
    exit 0
fi

# Parse DATABASE_URL: postgresql://user:pass@host:port/dbname
DB_USER=$(echo "$DATABASE_URL" | sed -n 's|.*://\([^:@]*\).*|\1|p')
DB_PASS=$(echo "$DATABASE_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')

# Default to postgres if empty
DB_USER=${DB_USER:-postgres}
DB_NAME=${DB_NAME:-postgres}

echo "Setting up database for user: $DB_USER, database: $DB_NAME"

# Create user if not postgres
if [ "$DB_USER" != "postgres" ]; then
    psql -v ON_ERROR_STOP=0 --username postgres <<-EOSQL
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
                CREATE ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASS' SUPERUSER;
                RAISE NOTICE 'Created user: $DB_USER';
            END IF;
        END
        \$\$;
EOSQL
fi

# Create database if not postgres
if [ "$DB_NAME" != "postgres" ]; then
    psql -v ON_ERROR_STOP=0 --username postgres <<-EOSQL
        SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec
EOSQL
fi

echo "Database setup complete!"
