## Rajniti

Indian election + politician data project with a **JSON-first data layer** and an **agentic enrichment layer** (LLM-powered).

### What lives where

- **JSON data (source of truth)**: `app/data/mp.json`, `app/data/mla.json`
- **Agentic enrichment (writes back to JSON)**: `app/agents/`
- **Prompt builders**: `app/prompts/`
- **Mini cache (skip already-processed politician IDs)**: `app/database/cache.db` (SQLite)

### Current enrichment coverage

- **Education**: implemented (stored as an array in schema + JSON)
- More fields (family, crime, contact, social, etc.) can be added as new process classes.

## Quick start (backend)

### Requirements

- **Python**: 3.9+

### Setup (one simple install)

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

To install test/dev-only tools (optional):

```bash
. venv/bin/activate
pip install -r requirements-test.txt
```

### Update / upgrade dependencies

```bash
. venv/bin/activate
pip install -U -r requirements.txt
```

### Run API

```bash
make run
```

---

## Agentic enrichment (how to fill politician details)

The enrichment pipeline:

- Reads MPs/MLAs from JSON (`PoliticianService`)
- Skips any politician ID already in SQLite cache (unless `--force`)
- Runs available processes (currently only **Education**)
- Persists updates back to `mp.json` / `mla.json`

### Run the politician agent

- **All politicians (MP + MLA)**:

```bash
python3 scripts/run_politician_agent.py
```

- **Only MPs**:

```bash
python3 scripts/run_politician_agent.py --type MP
```

- **Only MLAs**:

```bash
python3 scripts/run_politician_agent.py --type MLA
```

- **Single politician by ID**:

```bash
python3 scripts/run_politician_agent.py --id "<POLITICIAN_ID>"
```

- **Force re-run (ignore cache)**:

```bash
python3 scripts/run_politician_agent.py --type MP --force
```

- **Limit processed (useful for testing)**:

```bash
python3 scripts/run_politician_agent.py --type MP --limit 5
```

### Logging (recommended)

```bash
python3 scripts/run_politician_agent.py --type MP --limit 3 --log-level DEBUG
```

---

## LLM providers (Gemini primary, Perplexity / OpenAI fallback)

Agents use a **failover LLM client** (`app/config/agent_config.py`):

- Provider order comes from `AGENT_LLM_PROVIDERS`
- If a provider hits quota/rate limits, it falls back to the next provider
- Gemini quota errors (`ResourceExhausted`, 429) are handled and put into cooldown before fallback

### Configure providers in `.env`

```bash
# Provider priority order (first = preferred)
AGENT_LLM_PROVIDERS=gemini,perplexity,openai

# API keys
PERPLEXITY_API_KEY=pplx-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Models
AGENT_PERPLEXITY_MODEL=sonar
AGENT_OPENAI_MODEL=gpt-4o-mini
AGENT_GEMINI_MODEL=gemini-2.5-flash
```

### Gemini dependencies

Already included in `requirements.txt` (no extra install needed).

---

## Contributing (fill missing details + raise PR)

We want contributors to help populate missing politician fields safely and consistently.

### Contribution workflow

- **Pick a scope**: MPs or MLAs, or a specific state/segment (start small)
- **Run the agent with a small limit** to verify your environment and outputs:

```bash
python3 scripts/run_politician_agent.py --type MP --limit 3 --log-level INFO
```

- **Run larger batch** when confident:

```bash
python3 scripts/run_politician_agent.py --type MP --log-level INFO
```

### Important rules

- **Never commit secrets**:
    - Do not commit `.env`
    - Do not commit any API keys
- **Cache is local**:
    - `app/database/cache.db` is a local SQLite file; do not commit it
- **Data changes are the PR**:
    - Your PR should primarily include updates to:
        - `app/data/mp.json` and/or `app/data/mla.json`

### Adding a new enrichment process (extensible)

- Add prompt builder to: `app/prompts/politician_prompts.py`
- Add a new process class in: `app/agents/politician_agent.py`
- Register it in `PoliticianAgent.__init__` by appending to `self.processes`

---

## Contributing: add MLAs for a state

If you'd like to help populate MLAs for a state, run the agent locally with your own API keys and open a PR with the updated JSON data.

1. Fork the repo and create a branch:

```bash
git clone <your-fork-url>
cd Rajniti
git checkout -b add-mlas-<STATE>
```

2. Setup locally:

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

3. Obtain API keys

- Gemini (Google Generative AI):
  - In Google Cloud Console enable the "Generative AI API" (sometimes listed as Gemini / Generative models).
  - Go to APIs & Services → Credentials → Create credentials → API key.
  - Copy the key and add to your local `.env` as `GEMINI_API_KEY=<your-key>`.
  - Note: billing/quota rules apply; free tier limits are strict.

- Alternatives:
  - You may set `OPENAI_API_KEY` or `PERPLEXITY_API_KEY` and adjust `AGENT_LLM_PROVIDERS`.

4. Configure environment (do NOT commit `.env`)

```bash
cp .env.example .env
# edit .env and set GEMINI_API_KEY (and others as needed)
export AGENT_LLM_PROVIDERS=gemini,perplexity,openai
```

5. Generate MLAs for a state

```bash
. venv/bin/activate
python3 scripts/fetch_mlas.py --state "Andhra Pradesh" --log-level INFO
```

- Omit `--state` to run for all states (long-running).

6. Inspect and commit changes

- Review `app/data/mla.json` and only commit the updated JSON file(s) with the new/updated MLA records.
- Never commit `.env` or API keys.

```bash
git add app/data/mla.json
git commit -m "Add/refresh MLA data for <STATE>"
git push -u origin add-mlas-<STATE>
```

7. Open a Pull Request

- Create a PR to upstream `main`. In the PR body include:
  - Summary: state name, number of MLAs added/updated
  - How tested: `python3 scripts/fetch_mlas.py --state "<STATE>"` (attach logs/snippets)
  - Notes: any uncertain records or manual fixes performed

Thanks — maintainers will review and merge valid additions.

## Testing

```bash
make test
```

---

## Project structure (high-level)

```
app/
  agents/              # Agentic enrichment layer (writes to JSON)
  prompts/             # Prompt builders (LLM input)
  data/                # JSON data layer (source of truth)
  core/                # shared utilities (logger, cache, errors)
  services/            # read/write services over JSON + other services
scripts/
  run_politician_agent.py
```
