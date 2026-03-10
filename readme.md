<div align="center">

# 🏛️ Rajniti

**Open-source Indian politician data platform — powered by AI enrichment**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=flat&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![Flask](https://img.shields.io/badge/Flask-REST_API-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Agents-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)

<br />

Browse, search, and explore data on Indian MPs and MLAs.  
Enrich politician profiles automatically using LLM-based agents.

[Getting Started](#-getting-started) · [Contributing with AI](#-contributing-with-ai) · [API Reference](#-api-endpoints) · [Project Structure](#-project-structure)

</div>

---

## ✨ Features

| | Feature | Description |
|---|---|---|
| 🔍 | **Search & Browse** | Look up MPs and MLAs by name, state, constituency, or party |
| 🤖 | **AI Enrichment** | Automatically fill education, family, criminal records, and more using LLMs |
| 🔄 | **Multi-Model Failover** | Gemini → OpenAI → Perplexity with per-model cooldown on rate limits |
| 🗃️ | **JSON-First Data** | Source of truth lives in version-controlled JSON files |
| 🧠 | **Vector Search** | Ask natural-language questions about politicians (ChromaDB) |
| 🔐 | **Google OAuth** | User accounts via NextAuth with backend sync |
| 📊 | **Stats Dashboard** | Party breakdown, state coverage, and enrichment progress |

---

## 🏗️ Tech Stack

<table>
<tr>
<td align="center" width="50%">

**Backend**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

</td>
<td align="center" width="50%">

**Frontend**

![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

</td>
</tr>
<tr>
<td align="center">

**AI / LLM**

![Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)

</td>
<td align="center">

**Infrastructure**

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GCP](https://img.shields.io/badge/Cloud_Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)

</td>
</tr>
</table>

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| Docker | Latest (optional, for Postgres) |

### 1. Clone & Install

```bash
git clone https://github.com/<your-username>/Rajniti.git
cd Rajniti

# Backend (runs via Python venv)
make install            # creates venv + installs deps
cp .env.example .env    # configure your environment
. venv/bin/activate     # activate the virtual environment

# Frontend
cd frontend && npm install
```

Backend commands (`make run`, `make test`, db and lint targets) use the project **virtualenv** (`venv/`) automatically. To run Python scripts by hand, either use those Make targets or activate the venv first: `source venv/bin/activate` (or `make venv` for an interactive shell with venv active).

### 2. Configure Environment

Copy `.env.example` and fill in the required values:

```bash
# Backend — .env
FLASK_ENV=development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/rajniti   # optional
GEMINI_API_KEY=your-key-here          # free tier — only key you need to get started

# Frontend — frontend/.env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run

```bash
# Option A: Docker (backend + Postgres)
make dev

# Option B: Run backend directly (via venv)
make run                # starts Flask API on :8000 (uses project venv)

# Frontend (separate terminal)
make frontend           # starts Next.js on :3000
```

To run other Python commands in the project venv, use `make venv` to open a shell with the venv activated, or run `source venv/bin/activate` in your terminal first.

### 4. Verify

Open `http://localhost:8000/api/v1/health` — you should see a healthy response.

---

## 🤖 Contributing with AI

> **This is the easiest way to contribute.** Run AI agents locally with your own API keys, and open a PR with enriched politician data.

### How It Works

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐     ┌──────────────┐
│  JSON Data   │────▶│  LLM Agents   │────▶│  Enriched    │────▶│  Open a PR   │
│  (mp/mla)    │     │  (Gemini/GPT) │     │  JSON Data   │     │              │
└──────────────┘     └───────────────┘     └──────────────┘     └──────────────┘
```

The enrichment pipeline reads politicians from JSON, queries LLMs for missing details (education, family, criminal records, etc.), and writes the results back. A local SQLite cache prevents re-processing.

### Step-by-Step

**1. Fork & set up**

```bash
git clone <your-fork-url>
cd Rajniti
git checkout -b enrich/<scope>       # e.g. enrich/mp-education
make install
cp .env.example .env                 # add your API key(s)
```

**2. Get an API key** (at least one)

| Provider | How to Get a Key | Env Variable | Cost |
|----------|-----------------|--------------|------|
| **Gemini** | [Google AI Studio](https://aistudio.google.com/apikey) | `GEMINI_API_KEY` | **Free tier** (rate-limited) |
| **OpenAI** | [platform.openai.com](https://platform.openai.com/api-keys) | `OPENAI_API_KEY` | Paid |
| **Perplexity** | [perplexity.ai](https://www.perplexity.ai/settings/api) | `PERPLEXITY_API_KEY` | Paid |

> **Fastest setup:** Get a free Gemini key from [Google AI Studio](https://aistudio.google.com/apikey), paste it as `GEMINI_API_KEY` in your `.env`, and you're ready to run agents — no paid key needed.

Models fail over automatically (Gemini → OpenAI → Perplexity). Order is configured in `app/config/agent_config.py`.

**3. Run the agent**

```bash
# Run the agent for all politicians
python3 scripts/run_politician_agent.py

# Test with a small batch first
python3 scripts/run_politician_agent.py --type MP --limit 3 --log-level INFO

# Run for all MPs
python3 scripts/run_politician_agent.py --type MP --log-level INFO

# Run for all MLAs
python3 scripts/run_politician_agent.py --type MLA --log-level INFO

# Target a single politician
python3 scripts/run_politician_agent.py --id "<POLITICIAN_ID>"

# Force re-run (ignore cache)
python3 scripts/run_politician_agent.py --type MP --force
```

**4. Add MLAs for a new state**

```bash
python3 scripts/fetch_mlas.py --state "Andhra Pradesh" --log-level INFO
```

**5. Open a PR**

```bash
git add app/data/mp.json app/data/mla.json
git commit -m "Enrich MP education data"
git push -u origin enrich/<scope>
```

Then open a Pull Request. Include: the state/scope, number of records, and how you tested.

---

## 🛡️ Contribution Rules

> **These rules are non-negotiable for all PRs.**

| Rule | Details |
|------|---------|
| **No secrets** | Never commit `.env` or API keys |
| **No cache files** | `app/database/cache.db` is local-only |
| **Data PRs only touch JSON** | Your PR should update `app/data/mp.json` and/or `app/data/mla.json` |
| **Tests must pass** | Run `make test` before pushing |
| **Review your diff** | Ensure only intended changes are included |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/politicians` | List politicians (filter by type) |
| `GET` | `/api/v1/politicians/search?q=` | Search by name |
| `GET` | `/api/v1/politicians/<id>` | Get a single politician |
| `GET` | `/api/v1/politicians/state/<state>` | Filter by state |
| `GET` | `/api/v1/politicians/party/<party>` | Filter by party |
| `GET` | `/api/v1/stats` | Summary statistics |
| `GET` | `/api/v1/states` | List all states |
| `GET` | `/api/v1/parties` | List all parties |
| `POST` | `/api/v1/questions/ask` | Ask a question (vector search) |
| `GET` | `/api/v1/health` | Health check |

---

## 🧩 Adding a New Enrichment Process

Want to enrich a new field (e.g., criminal records, social media)?

1. **Add a prompt builder** in `app/prompts/politician_prompts.py`
2. **Create a process class** in `app/agents/politician_agent.py`
3. **Register it** in `PoliticianAgent.__init__` by appending to `self.processes`

The architecture is designed to be extensible — each enrichment field is an independent process.

---

## 🧪 Testing

```bash
make test              # all tests
make test-unit         # unit tests only
make test-e2e          # end-to-end tests
make coverage          # tests + coverage report
make lint              # backend + frontend linting
make format            # auto-format with Black + isort
```

---

## 📂 Project Structure

```
Rajniti/
├── app/
│   ├── agents/            # LLM-based enrichment agents
│   ├── config/            # Agent & provider configuration
│   ├── controllers/       # API request handlers
│   ├── core/              # Utilities, logging, errors
│   ├── data/              # mp.json, mla.json (source of truth)
│   ├── database/          # Models, migrations, SQLite cache
│   ├── prompts/           # LLM prompt builders
│   ├── routes/            # Flask route definitions
│   ├── schemas/           # Pydantic validation schemas
│   └── services/          # Business logic layer
├── frontend/
│   ├── app/               # Next.js App Router pages
│   ├── components/        # React components
│   ├── data/              # Generated static data (contributors.json)
│   ├── hooks/             # Custom React hooks
│   └── lib/               # Shared utilities
├── scripts/               # CLI scripts (agent runner, DB, MLA fetcher)
├── tests/                 # Unit, integration, and E2E tests
├── alembic/               # Database migrations
├── docker/                # Docker init scripts
├── .github/
│   ├── workflows/         # CI/CD (lint, test, release)
│   └── PULL_REQUEST_TEMPLATE.md
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── pyproject.toml
```

---

## ⚙️ LLM Provider Configuration

Agents use a **failover LLM client** with automatic per-model cooldown:

- Models are tried top-to-bottom from `PROVIDER_CONFIGS` in `app/config/agent_config.py`
- If a model hits a rate limit (429), it enters cooldown and the next model is used
- Cooldown is per-model — `gemini-1.5-flash` cooling doesn't block `gemini-2.0-flash`
- Only API keys go in `.env`; model names and order are configured in code

---

## 🐳 Docker

```bash
make dev       # Local Postgres + API (development)
make prod      # API only, expects external Postgres (e.g. Supabase)
make stop      # Stop all containers
make clean     # Remove containers + volumes
make reset     # Full reset (wipes data, fresh start)
```

---

## 👥 Contributors

Contributors are highlighted on the website at [`/contributors`](https://rajniti.in/contributors).

**How it works:**

- `scripts/generate_contributors.py` fetches contributor data from the GitHub API and writes `frontend/data/contributors.json`.
- A GitHub Actions workflow (`.github/workflows/update_contributors.yml`) runs weekly (Monday midnight UTC) and on manual dispatch to keep the file up to date. It only commits when the data has actually changed.
- The frontend reads the static JSON at build time — no runtime GitHub API calls.

**Running locally:**

```bash
# Generate/refresh contributors data (optional GITHUB_TOKEN for higher rate limits)
python scripts/generate_contributors.py

# With a token
GITHUB_TOKEN=ghp_... python scripts/generate_contributors.py
```

---

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

<div align="center">

**Built with care for Indian democracy** 🇮🇳

[Report a Bug](../../issues/new) · [Request a Feature](../../issues/new) · [Contribute Data](#-contributing-with-ai)

</div>
