# 🗳️ Rajniti

> Indian Election Data API — Flask + PostgreSQL + Next.js

## Quick Start

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/your-username/rajniti.git
cd rajniti

# Start API + PostgreSQL
docker compose --profile local-db up -d --build

# API: http://localhost:8000
# Health: http://localhost:8000/api/v1/health
```

### Option 2: Local Python + Supabase/Postgres

```bash
git clone https://github.com/your-username/rajniti.git
cd rajniti

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set database URL (Supabase or local Postgres)
export DATABASE_URL="postgresql://user:password@localhost:5432/rajniti"

# Run
python run.py
```

---

## Environment Variables

Create a `.env` file in the project root:

```bash
# Required for Docker
POSTGRES_USER=rajniti
POSTGRES_PASSWORD=rajniti_dev_password
POSTGRES_DB=rajniti
DATABASE_URL=postgresql://rajniti:rajniti_dev_password@postgres:5432/rajniti

# Optional
SECRET_KEY=your-secret-key
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=8000
PERPLEXITY_API_KEY=your-api-key
OPENAI_API_KEY=your-api-key

# Auto-populate settings (enabled by default)
AUTO_POPULATE_DB=true
AUTO_POPULATE_LIMIT=500
```

---

## Database Setup

### Install PostgreSQL

**macOS:**
```bash
brew install postgresql
brew services start postgresql
createdb rajniti
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
sudo -u postgres createdb rajniti
```

### Connect & View Data

```bash
# Connect to database
psql -U postgres -d rajniti

# Common commands
\dt                     # List tables
\d candidates           # Describe table
SELECT COUNT(*) FROM candidates;
SELECT * FROM candidates LIMIT 10;
\q                      # Exit
```

### Docker PostgreSQL Shell

```bash
# Connect to running container
docker exec -it rajniti-postgres psql -U rajniti -d rajniti

# Same commands work inside
\dt
SELECT * FROM parties LIMIT 5;
\q
```

---

## Data Migration

### Auto-Population (Default)

On startup, the app automatically seeds the database with sample election data if empty. Control via:

```bash
AUTO_POPULATE_DB=true        # Enable/disable (default: true)
AUTO_POPULATE_LIMIT=500      # Number of candidates to load
```

### Manual Migration

```bash
# Activate venv
source venv/bin/activate

# Initialize tables
python scripts/db.py init

# Migrate JSON data to database
python scripts/db.py migrate

# Preview without changes
python scripts/db.py migrate --dry-run

# Sync model changes
python scripts/db.py sync

# Reset database (WARNING: deletes all data)
python scripts/db.py reset
```

---

## Frontend

```bash
cd frontend
npm install
npm run dev
# http://localhost:3000
```

Deploy to Vercel: Set **Root Directory** to `frontend`.

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/health` | Health check |
| `GET /api/v1/elections` | List elections |
| `GET /api/v1/candidates/search?q=modi` | Search candidates |
| `GET /api/v1/parties` | List parties |
| `GET /api/v1/questions` | Predefined questions |
| `POST /api/v1/questions/ask` | Ask a question |

Full docs: `GET /api/v1/doc`

---

## Project Structure

```
rajniti/
├── app/
│   ├── controllers/     # Business logic
│   ├── database/        # Models, migrations
│   ├── routes/          # API endpoints
│   ├── services/        # Data access
│   └── data/            # JSON election data
├── frontend/            # Next.js app
├── scripts/             # CLI utilities
├── alembic/             # DB migrations
├── docker-compose.yml
└── run.py
```

---

## Commands

```bash
# Docker
docker compose --profile local-db up -d --build   # Start
docker compose logs -f rajniti-api                # Logs
docker compose down                               # Stop
docker compose down -v                            # Stop + remove volumes

# Local
python run.py                                     # Run dev server
python scripts/db.py init                         # Init DB
python scripts/db.py migrate                      # Migrate data
pytest tests/ -v                                  # Run tests
```

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and test
4. Submit a pull request

---

## License

MIT
