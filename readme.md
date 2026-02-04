# 🗳️ Rajniti

**Indian Election Intelligence API** — Real-time candidate data, LLM-powered Q&A, semantic search.

[![Python](https://img.shields.io/badge/Python-3.9+-3776ab?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000?logo=flask)](https://flask.palletsprojects.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000?logo=next.js)](https://nextjs.org)

---

## Architecture

**JSON-First Design**: Election data (candidates, parties, constituencies) is stored in JSON files and served directly via API. Only user authentication data is stored in PostgreSQL.

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Scrapers      │────▶│   JSON Files     │◀────│  Candidate      │
│   (Manual)      │     │   (app/data/)    │     │  Agent (LLM)    │
└─────────────────┘     └────────┬─────────┘     └────────┬────────┘
                                 │                        │
                                 ▼                        ▼
                        ┌────────────────┐       ┌────────────────┐
                        │ JsonDataService│       │   ChromaDB     │
                        │    (API)       │       │ (Vector Search)│
                        └────────────────┘       └────────────────┘
```

---

## Quick Start

```bash
# Clone & setup
git clone https://github.com/your-username/rajniti.git && cd rajniti
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run API (no database required for election data!)
python run.py

# DB Connect
brew services start postgresql
psql -h localhost -p 5432 -U imsks -d rajniti
```

**API:** http://localhost:8000 | **Health:** http://localhost:8000/api/v1/health

---

## Workflows

### 1. Scrape Election Data

```bash
# Vidhan Sabha
python scripts/scrape_election.py --url https://results.eci.gov.in/ResultAcGenNov2025 --type vidhan-sabha
```

Data saved to `app/data/{lok_sabha|vidhan_sabha}/{election-id}/`

### 2. Enrich Candidates with LLM

```bash
# Fetch detailed candidate info (education, assets, crime cases, etc.)
python scripts/run_candidate_agent.py --election-id lok-sabha-2024 --batch-size 10

# Options
--provider openai      # LLM provider (perplexity, openai)
--disable-cache        # Skip response caching
--dry-run              # Preview without changes
```

### 3. Sync to Vector DB

```bash
# Sync candidates to ChromaDB for semantic search
python scripts/sync_candidates_to_vector_db.py --election-id lok-sabha-2024

# Options
--winners-only         # Only winning candidates
--state DL             # Filter by state
--dry-run              # Preview without changes
```

---

## Environment Variables

Create `.env` file:

```bash
# Required for user auth (optional if not using auth features)
DATABASE_URL=postgresql://user:pass@localhost:5432/rajniti

# LLM providers (for candidate enrichment)
PERPLEXITY_API_KEY=pplx-...
OPENAI_API_KEY=sk-...
LLM_PROVIDER=perplexity  # or openai

# Optional
FLASK_PORT=8000
SECRET_KEY=your-secret-key
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/elections` | List all elections |
| `GET /api/v1/elections/{id}` | Get election details |
| `GET /api/v1/candidates/search?q=modi` | Search candidates |
| `GET /api/v1/candidates/{election_id}/{id}` | Get candidate details |
| `GET /api/v1/parties/{election_id}` | List parties |
| `GET /api/v1/constituencies/{election_id}` | List constituencies |
| `POST /api/v1/questions/ask` | Ask LLM about elections |

---

## Testing

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test files
pytest tests/unit/services/test_json_data_service.py -v
```

---

## Project Structure

```
rajniti/
├── app/
│   ├── controllers/         # Business logic
│   ├── database/            # User model only
│   │   └── models/user.py
│   ├── routes/              # API endpoints
│   ├── services/
│   │   ├── json_data_service.py   # JSON file data access
│   │   ├── candidate_agent.py     # LLM enrichment
│   │   └── vector_db_pipeline.py  # ChromaDB sync
│   ├── scrapers/            # Election data scrapers
│   └── data/                # JSON data files
│       ├── elections/       # Election metadata
│       ├── lok_sabha/       # Lok Sabha data
│       └── vidhan_sabha/    # Vidhan Sabha data
├── frontend/                # Next.js app
├── scripts/                 # CLI tools
├── tests/                   # pytest suite
└── chroma_db/              # Vector database
```

---

## Data Flow

1. **Scrapers** fetch election data from ECI and save to JSON files
2. **Candidate Agent** enriches data using LLM and saves back to JSON + ChromaDB
3. **JsonDataService** serves data via Flask API
4. **ChromaDB** provides semantic search capabilities

---

## Deploy

**Backend → Docker/Cloud Run**
```bash
docker build -t rajniti .
docker run -p 8000:8000 -v ./app/data:/app/app/data rajniti
```

**Frontend → Vercel**
```bash
cd frontend && vercel --prod
```

---

## License

MIT
