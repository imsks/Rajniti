# 🗳️ Rajniti

**Indian Election Intelligence API** — Real-time candidate data, LLM-powered Q&A, semantic search.

[![Python](https://img.shields.io/badge/Python-3.9+-3776ab?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000?logo=flask)](https://flask.palletsprojects.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000?logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Flask, SQLAlchemy, Alembic, Gunicorn |
| **Frontend** | Next.js 15, TypeScript, TailwindCSS |
| **Database** | PostgreSQL 16, Supabase (prod) |
| **AI/Search** | OpenAI, Perplexity, ChromaDB |
| **Infra** | Docker, GCP Cloud Run, Vercel |

---

## Quick Start

```bash
# Clone & setup
git clone https://github.com/your-username/rajniti.git && cd rajniti

# Create .env (see below)
make dev        # Docker + local Postgres
# OR
make run        # Local Python (requires DATABASE_URL)
```

**API:** http://localhost:8000 | **Health:** http://localhost:8000/api/v1/health

---

## Environment

Create `.env` file:

```bash
# Any user/database works - auto-created on first run!
DATABASE_URL=postgresql://myuser:mypass@postgres:5432/mydb

# Or just use defaults
DATABASE_URL=postgresql://postgres@postgres:5432/postgres

# Supabase (production)
DATABASE_URL=postgresql://postgres.[ref]:[pw]@pooler.supabase.com:6543/postgres

# Optional
FLASK_PORT=8000
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
```

---

## Commands

```bash
make dev              # Start with local Postgres (Docker)
make prod             # Start with Supabase (Docker)
make run              # Local Python server
make reset            # Clean volumes + restart (fixes credential issues)
make test             # Run all tests
make coverage         # Tests + coverage report
make logs             # Tail Docker logs
make clean            # Remove containers + volumes
```

Run `make help` for all commands.

---

## API

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/elections` | List elections |
| `GET /api/v1/candidates/search?q=modi` | Search candidates |
| `GET /api/v1/parties` | List parties |
| `POST /api/v1/questions/ask` | Ask LLM about elections |

Docs: `GET /api/v1/doc`

---

## Testing

```bash
make test             # All tests
make test-unit        # Unit only
make test-e2e         # E2E only
make coverage         # With coverage
make lint             # Code quality
```

**Coverage Target:** 60%+ | **Test Types:** Unit, Integration, E2E

---

## Project Structure

```
rajniti/
├── app/
│   ├── controllers/    # Business logic
│   ├── database/       # Models, migrations
│   ├── routes/         # API endpoints
│   ├── services/       # LLM, search, data
│   └── data/           # Election JSON
├── frontend/           # Next.js app
├── tests/              # pytest suite
├── alembic/            # DB migrations
└── Makefile            # All commands
```

---

## Database

```bash
# Docker shell
docker exec -it rajniti-postgres psql -U rajniti -d rajniti

# Migrations
make db-init          # Create tables
make db-migrate       # Run migrations
make db-reset         # Reset (⚠️ deletes data)
```

---

## Deploy

**Backend → GCP Cloud Run**
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

**Frontend → Vercel**
```bash
cd frontend && vercel --prod
```

---

## License

MIT
