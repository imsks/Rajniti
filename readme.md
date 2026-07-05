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

## Pick a setup path

| Goal | Command | What you get |
|------|---------|--------------|
| **Fastest — API only (Docker)** | `make dev-api` | Flask API `:8000` + Postgres |
| **Full stack (Docker)** | `make dev` | API `:8000` + Next.js `:3000` + Postgres |
| **API only (local venv)** | `make install && make db-migrate && make run` | Flask on `:8000` (bring your own Postgres) |
| **Full stack (local)** | above + `make frontend-dev` | API + frontend, no Docker |

> **Port note:** API defaults to `:8000`. macOS reserves `:5000` for AirPlay.

---

## Quick Start — Docker (recommended)

**Prerequisites:** Docker Desktop (or Docker Engine + Compose v2).

```bash
git clone https://github.com/imsks/Rajniti.git && cd Rajniti
make setup              # copies .env.example → .env, frontend/.env.example → frontend/.env
make install-hooks      # one-time: auto-stamps lastUpdated on politician data commits
make dev-api            # fastest: API + Postgres (skip frontend image build)
# — or —
make dev                # full stack: API + Next.js + Postgres
```

**Verify**

```bash
curl http://localhost:8000/api/v1/health          # API
open http://localhost:3000                         # frontend (make dev only)
```

**First `make dev` note:** The frontend image builds in seconds; `npm ci` runs **once at container start** (not during `docker build`), so you may see “installing dependencies…” for a few minutes the first time. Later starts reuse the `node_modules` volume and are much faster.

**Subsequent runs** (skip rebuild):

```bash
make dev BUILD=0
# or
make dev-api BUILD=0
```

---

## Quick Start — Local (no Docker)

**Prerequisites:** Python 3.11+, Node 20+, a running PostgreSQL instance.

```bash
git clone https://github.com/imsks/Rajniti.git && cd Rajniti
make setup
make install            # venv + pip deps
make install-hooks
# Edit .env — set DATABASE_URL to your local Postgres, e.g.:
#   DATABASE_URL=postgresql://user:pass@localhost:5432/rajniti
make db-migrate
make run                # API on :8000
```

**Frontend (separate terminal):**

```bash
make frontend-install   # first time only
make frontend-dev       # http://localhost:3000
```

Copy `frontend/.env.example` → `frontend/.env` (via `make setup`) and set `NEXTAUTH_*` / Google OAuth for sign-in.

---

## Makefile reference

Run `make help` anytime. All targets:

| Command | Description |
|---------|-------------|
| `make help` | List all commands |
| `make setup` | Copy `.env` templates (safe to re-run) |
| `make install` | Create `venv/` + install Python deps |
| `make install-dev` | `install` + test/lint deps (`requirements-test.txt`) |
| `make install-hooks` | Git pre-commit hook for `lastUpdated` on data files |
| `make run` | Local Flask API (`:8000`, uses venv) |
| `make frontend-install` | `npm ci` in `frontend/` |
| `make frontend-dev` | Local Next.js dev server (`:3000`) |
| `make dev` | Docker: API + frontend + Postgres |
| `make dev-api` | Docker: API + Postgres only (**fastest Docker path**) |
| `make dev-build` | Rebuild Docker images without starting |
| `make stop` | Stop Docker containers |
| `make logs` | Tail logs (`SERVICE=rajniti-api` optional) |
| `make prod` | Production API image (Supabase `DATABASE_URL`) |
| `make db-migrate` | Alembic upgrade head (local venv) |
| `make db-reset` | Stop Docker + **delete** local Postgres volume |
| `make test` | Backend + frontend tests |
| `make test SUITE=unit` | Unit tests only |
| `make test SUITE=integration` | Integration tests only |
| `make test SUITE=e2e` | E2E tests only |
| `make test COV=1` | Backend tests with coverage |
| `make lint` | Python + frontend linters |
| `make format` | Auto-format Python (black + isort) |

**Useful variables:** `BUILD=0` (skip image rebuild), `SUITE=unit|integration|e2e`, `COV=1`, `SERVICE=rajniti-web`.

---

## Environment variables

See [`.env.example`](.env.example) and [`frontend/.env.example`](frontend/.env.example).

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `GEMINI_API_KEY` | Yes* | Google Gemini (free tier works) |
| `PERPLEXITY_API_KEY` | No | Perplexity fallback |
| `OPENAI_API_KEY` | No | OpenAI fallback |
| `AGENT_LLM_PROVIDERS` | No | Failover order (default: `gemini,perplexity,openai`) |

\* At least one LLM key is needed for enrichment agents. The API itself runs without one.

**`DATABASE_URL` by environment**

| Setup | Value |
|-------|-------|
| Docker (`make dev` / `make dev-api`) | `postgresql://rajniti:rajniti@postgres:5432/rajniti` |
| Local venv → Docker Postgres | `postgresql://rajniti:rajniti@localhost:5432/rajniti` |
| Beekeeper / host tools | host `localhost`, port `5432`, user `rajniti`, db `rajniti` |
| Supabase (`make prod`) | Session-mode pooler URL (port `5432`) |

**Beekeeper: `role "postgres" does not exist`?**  
Homebrew Postgres may be bound to `localhost:5432` instead of Docker. Stop it: `brew services stop postgresql@17`, then reconnect. Only one Postgres can own that port.

---

## Running agents

Agents enrich politician data (education, career, citations). Add at least one LLM key to `.env` (Gemini free tier works).

```bash
source venv/bin/activate

# Politician enrichment
python scripts/run_politician_agent.py --type MP --limit 3   # small batch first
python scripts/run_politician_agent.py --type MP             # all MPs
python scripts/run_politician_agent.py --type MLA --force    # re-enrich

# Citations
python scripts/run_citation_agent.py --type MP --limit 10

# MLA fetcher
python scripts/fetch_mlas.py --state "Karnataka"
```

**Tips:** Use `--limit` to avoid Gemini rate limits. Citation agent checkpoints progress. `--log-level DEBUG` for verbose LLM logs.

---

## Manual setup (venv)

If you prefer not to use `make install`:

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # set DATABASE_URL + optional LLM keys
source venv/bin/activate && alembic upgrade head
python run.py                   # http://localhost:8000
curl http://localhost:8000/api/v1/health
```

---

## Project structure

```
app/
├── agents/         # LLM enrichment (politician, citation, MLA fetcher)
├── config/         # LLM failover (FreeTierLLM)
├── controllers/    # Request handlers
├── core/           # Cache, logging, exceptions
├── data/           # mp.json, mla.json — source of truth
├── database/       # SQLAlchemy models, session
├── prompts/        # LLM prompt templates
├── routes/         # Flask routes
├── schemas/        # Pydantic validation
├── scrapers/       # ECI election scraper
├── services/       # Business logic
└── tools/          # Web search, Wikipedia (used by agents)

scripts/            # CLI: agents, DB, MLA fetcher
tests/              # Unit, integration, E2E (pytest)
frontend/           # Next.js — see frontend/README.md
```

---

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/politicians` | List (`?type=MP\|MLA`) |
| `GET` | `/api/v1/politicians/search?q=` | Search by name/state/party |
| `GET` | `/api/v1/politicians/<id>` | Single politician |
| `GET` | `/api/v1/politicians/state/<state>` | Filter by state |
| `GET` | `/api/v1/politicians/party/<party>` | Filter by party |
| `GET` | `/api/v1/stats` | Summary statistics |
| `GET` | `/api/v1/health` | Health check |

---

## Database & migrations

PostgreSQL via SQLAlchemy + Alembic. Migrations run automatically on API startup in Docker.

```bash
make db-migrate
# After model changes:
python scripts/db.py autogenerate -m "add column_name"
# Review alembic/versions/, then:
make db-migrate
```

**Supabase:** Use the session-mode pooler URL (port `5432`), not the direct IPv6-only host.

---

## Politician data & `lastUpdated`

Records in `mp.json` / `mla.json` get `lastUpdated` stamped automatically on commit via the pre-commit hook:

```bash
make install-hooks
```

---

## Contributing with AI agents

```bash
git checkout -b enrich/<scope>
make setup                    # add Gemini key to .env

python scripts/run_politician_agent.py --type MP --limit 3
python scripts/run_citation_agent.py --type MP --limit 10

git add app/data/mp.json app/data/mla.json
git commit -m "Enrich MP education data"
git push -u origin enrich/<scope>
```

**Rules:** No secrets in commits. Data PRs should only change JSON. Run `make test` before pushing.

---

## Testing & CI

```bash
make install-dev              # first time
make test                     # all suites + frontend unit tests
make test SUITE=unit
make test COV=1
make lint
make format
```

PR CI: [`.github/workflows/ci.yml`](.github/workflows/ci.yml) — tests first, then lint and frontend build. Required check names: `Backend — tests`, `Frontend — tests`, `Backend — lint`, `Frontend — lint & typecheck`, `Frontend — production build`.

---

## License

[MIT](https://opensource.org/licenses/MIT)
