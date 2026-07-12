# Contributing to Rajniti

Thanks for helping build civic tech for political accountability in India.
Rajniti is built in public — issues, the [roadmap](./ROADMAP.md), and decisions
are all open.

## Table of contents

- [Ways to contribute](#ways-to-contribute)
- [Good first issues](#good-first-issues)
- [Repository layout](#repository-layout)
- [Local development](#local-development)
- [Module boundaries (backend)](#module-boundaries-backend)
- [Testing](#testing)
- [Code style & checks](#code-style--checks)
- [Pull requests](#pull-requests)

## Ways to contribute

- Fix a bug or pick up a [`good first issue`](#good-first-issues)
- Improve civic data quality (sources, corrections)
- Add tests (see the testing policy below)
- Improve docs

## Good first issues

New here? Start with an issue labelled **`good first issue`**:

- Browse them:
  <https://github.com/imsks/Rajniti/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22>
- Comment on the issue to claim it before starting, so we avoid duplicate work.
- We also use these companion labels:
  - **`good first issue`** — small, well-scoped, minimal context needed.
  - **`help wanted`** — we'd love a hand; may be larger than a first issue.
  - **`needs triage`** — not ready to pick up yet; maintainers will label it.
  - **`area: web` / `area: api`** — which app the issue touches.

Maintainers: keep `good first issue` items truly small (one clear change, clear
acceptance criteria, pointers to the relevant files).

## Repository layout

```
apps/
  web/      Next.js frontend (App Router, TS) — deploys to Vercel
  api/      Flask modular monolith (uv) — deploys to GCP Cloud Run
packages/
  tsconfig/        shared TypeScript config
  eslint-config/   shared ESLint config
```

The frontend consumes [`@sutra/ui`](https://www.npmjs.com/package/@sutra/ui) as
a public npm dependency — **do not build or vendor UI primitives**.

## Local development

Prerequisites: **Node 20+**, **pnpm 9+**, **Python 3.11+**, **uv**, and
**Docker** (for backing infra like ChromaDB).

```bash
git clone https://github.com/imsks/Rajniti.git
cd Rajniti
pnpm install            # installs JS deps for all workspaces
pnpm dev                # starts infra (chroma) + web + api
```

Per-app env files (copy and fill — never commit real secrets):

```bash
cp apps/web/.env.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env
```

Run a single side:

```bash
pnpm dev:web            # Next.js only
pnpm dev:api            # Flask only (http://localhost:8000)
```

## Module boundaries (backend)

The backend is a **modular monolith**. Modules (`promises`, `reps`, `rag`,
`agents`) are isolated and must only talk through each other's **public
facade** with **DTOs** — never by importing internals, ORM rows, or Chroma
handles.

Allowed dependency direction (enforced in CI by `import-linter`):

```
(promises, reps)  ->  rag  ->  agents
```

- `promises` and `reps` are siblings and **may not import each other**.
  Combine their data in the routes layer instead.
- `core` is shared infra and may be imported by anyone.
- Cross-module calls go through the package root, e.g.
  `from app.reps import RepsService` — not `from app.reps.internal...`.

If you need a new cross-module dependency, that's a design discussion — open an
issue rather than working around the boundary.

## Testing

**Policy: every line of testable code ships with tests** (unit, integration, or
e2e as appropriate). Run the suites before opening a PR.

Backend (`apps/api`):

```bash
pnpm --filter @rajniti/api test        # pytest (colocated unit + tests/ integration)
```

- Unit tests live **next to the module**: `app/<module>/tests/`.
- Integration / API-level tests live in `apps/api/tests/`.

Frontend (`apps/web`): Jest (unit/integration) + Playwright (e2e).

## Code style & checks

Run everything via Turborepo from the repo root:

```bash
pnpm lint          # ruff + import-linter (api), eslint (web)
pnpm typecheck     # pyright (api), tsc (web)
pnpm test          # all test suites
pnpm build         # production builds
```

Backend specifics: `ruff` for lint/format, `pyright` for types,
`import-linter` for boundaries. Type hints are expected everywhere.

## Pull requests

- Branch from `main`; keep PRs focused and small.
- CI runs per app (see `.github/workflows/ci-web.yml`, `ci-api.yml`) and must be
  green: build, lint, typecheck, tests, and module-boundary contracts.
- No secrets in commits. Use `.env` locally and the platform's secret manager in
  prod (Vercel env for web, GCP Secret Manager for the API).
- Describe the "why", link the issue, and note how you tested.

Deploys are independent: web via Vercel's Git integration, the API to Cloud Run
on merge to `main`.
