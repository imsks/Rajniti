<div align="center">

# Rajniti

**Open-source Indian politician data platform — powered by AI enrichment**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-REST_API-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)

</div>

---

## Quick Start (Docker — recommended)

```bash
git clone https://github.com/imsks/Rajniti.git && cd Rajniti
cp .env.example .env          # add at least one LLM API key
make dev                      # starts API + Postgres on :8000
```

Verify: `curl http://localhost:8000/api/v1/health`

## Quick Start (Local — no Docker)

**Prerequisites:** Python 3.11+, a running PostgreSQL instance.

```bash
git clone https://github.com/imsks/Rajniti.git && cd Rajniti
make install                  # creates venv/ and installs deps
cp .env.example .env          # edit DATABASE_URL to point at your local Postgres
make db-migrate               # apply migrations
make run                      # starts Flask on :8000
```

> **Port note:** The API defaults to port 8000. macOS reserves port 5000 for AirPlay.

---

## Environment Variables

See [`.env.example`](.env.example) for the full list. Key variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `GEMINI_API_KEY` | Yes* | Google Gemini (free tier works) |
| `PERPLEXITY_API_KEY` | No | Perplexity fallback |
| `OPENAI_API_KEY` | No | OpenAI fallback |
| `AGENT_LLM_PROVIDERS` | No | Comma-separated failover order (default: `gemini,perplexity,openai`) |

\* At least one LLM key is needed to run enrichment agents. The API itself works without one.

**Docker vs Local DATABASE_URL:**
- Docker (`make dev`): use `postgresql://postgres:postgres@postgres:5432/rajniti` (container hostname)
- Beekeeper / host tools: `localhost:5432`, user `postgres`, database `rajniti`

**Beekeeper fails with `role "postgres" does not exist`?**  
Two Postgres instances are fighting for port 5432. Homebrew Postgres (`postgresql@17`) binds `localhost:5432` and wins over Docker when you connect to `localhost`. Stop it:

```bash
brew services stop postgresql@17
```

Then reconnect in Beekeeper. Only one Postgres can own `localhost:5432`.

---

## Available Commands

```bash
make help          # Show all commands
```

| Command | Description |
|---------|-------------|
| `make install` | Create venv + install deps |
| `make install-dev` | + test/lint deps |
| `make dev` | Docker: API + local Postgres |
| `make prod` | Docker: API with Supabase |
| `make run` | Local Flask server (venv) |
| `make stop` | Stop all Docker containers |
| `make test` | Run all tests (`SUITE=unit` or `SUITE=e2e` for subset, `COV=1` for coverage) |
| `make lint` | black + isort + flake8 + mypy |
| `make format` | Auto-format code |
| `make db-migrate` | Run Alembic migrations |
| `make db-reset` | Reset database (deletes data) |

---

## Project Structure

```
app/
├── agents/         # LLM-based enrichment agents (politician, citation, MLA fetcher)
├── config/         # LLM failover wrapper (FreeTierLLM)
├── controllers/    # Request handlers
├── core/           # Utilities: cache, logging, exceptions, response helpers
├── data/           # mp.json, mla.json — source of truth
├── database/       # SQLAlchemy models, session, migration helpers
├── prompts/        # LLM prompt templates
├── routes/         # Flask route definitions
├── schemas/        # Pydantic validation
├── scrapers/       # ECI election result scraper
├── services/       # Business logic
└── tools/          # Web search, Wikipedia, generic scraper (used by agents)

scripts/            # CLI utilities: agent runner, DB management, MLA fetcher
tests/              # Unit, integration, E2E (pytest)
frontend/           # Next.js app (separate dev setup — see frontend/README.md)
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/politicians` | List politicians (filter by `?type=MP\|MLA`) |
| `GET` | `/api/v1/politicians/search?q=` | Search by name/state/party |
| `GET` | `/api/v1/politicians/<id>` | Single politician by ID |
| `GET` | `/api/v1/politicians/state/<state>` | Filter by state |
| `GET` | `/api/v1/politicians/party/<party>` | Filter by party |
| `GET` | `/api/v1/stats` | Summary statistics |
| `GET` | `/api/v1/health` | Health check |

---

## Database & Migrations

PostgreSQL via SQLAlchemy + Alembic. Migrations run automatically on server startup.

```bash
# After changing a model (e.g., adding a column):
python scripts/db.py autogenerate -m "add column_name to users"
# Review the generated file in alembic/versions/
make db-migrate
```

**Supabase note:** Use the session-mode pooler URL (port 5432), not the direct host (IPv6-only, fails in Docker).

---

## Contributing with AI Agents

The easiest way to contribute — run LLM agents locally and PR enriched data.

```bash
git checkout -b enrich/<scope>
cp .env.example .env                        # add your Gemini key (free)

# Enrich politicians
python scripts/run_politician_agent.py --type MP --limit 3    # test small batch
python scripts/run_politician_agent.py --type MP              # full run

# Add citation URLs
python scripts/run_citation_agent.py --type MP --limit 10

# Add MLAs for a new state
python scripts/fetch_mlas.py --state "Andhra Pradesh"

# Commit and PR
git add app/data/mp.json app/data/mla.json
git commit -m "Enrich MP education data"
git push -u origin enrich/<scope>
```

**Rules:** No secrets in commits. Only JSON data changes in data PRs. Run `make test` before pushing.

---

## Testing

```bash
make test                # all tests
make test SUITE=unit     # unit tests only
make test SUITE=e2e      # end-to-end only
make test COV=1          # with coverage report
make lint                # linters
make format              # auto-format
```

---

## License

[MIT](https://opensource.org/licenses/MIT)
