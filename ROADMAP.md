# Rajniti Roadmap

Rajniti is open-source civic tech for political accountability in India — ask
questions about your representatives, promises made vs kept, voting records, and
civic data, backed by a RAG pipeline and politician-specific agents.

This roadmap is intentionally public and evolves as the project does. Dates are
directional, not commitments. Have an idea? Open a
[discussion or issue](https://github.com/imsks/Rajniti/issues).

## Now — monorepo foundation

- [x] pnpm + Turborepo workspace (`apps/web`, `apps/api`, `packages/*`)
- [x] Flask modular monolith shell with enforced module boundaries
      (`promises`, `reps`, `rag`, `agents`)
- [x] `uv`-managed Python, `ruff` + `pyright` + `import-linter` in CI
- [x] Cloud Run Dockerfile (slim, non-root, fast cold start)
- [ ] Migrate existing `frontend/` → `apps/web` and backend → `apps/api`
- [ ] One-command local dev (`pnpm install && pnpm dev`)

## Next — product surface

- [ ] Promises: "made vs kept" tracking with sourced evidence
- [ ] Representatives: profiles, constituencies, voting records
- [ ] RAG Q&A over civic data with citations
- [ ] Politician-specific agents (request-scoped)
- [ ] Auth + saved questions (Supabase)

## Later — scale & trust

- [ ] Hosted vector index refresh pipeline (ingestion → baked image)
- [ ] Rate limiting (Upstash Redis) — only if needed
- [ ] Data provenance and correction workflow
- [ ] Public API for researchers and journalists
- [ ] Multi-language support (Hindi + regional languages)

## Principles

- **One backend.** A modular monolith, not microservices.
- **Boundaries are real.** Modules talk through public facades and DTOs; CI
  enforces it.
- **Reversible deploys.** Web on Vercel, API on Cloud Run — the API is
  containerized so the web can move to Cloud Run later if we consolidate.
- **Built in public.** Roadmap, issues, and decisions are open.
