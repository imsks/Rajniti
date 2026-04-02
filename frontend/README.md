# Rajniti Frontend

Next.js 16 (App Router) UI for browsing MPs/MLAs, dashboards, and onboarding. See the [root README](../readme.md) for the full stack and setup.

## Scripts

| Command | Description |
|--------|-------------|
| `npm run dev` | Start the dev server (http://localhost:3000) |
| `npm run build` | Production build |
| `npm run lint` | ESLint |
| `npx tsc --noEmit` | Typecheck (no emit) |
| `npm test` | Run all Jest tests (unit + integration; Playwright specs live under `__tests__/e2e/` and are excluded from Jest) |
| `npm run test:unit` | Jest unit tests only (`__tests__/lib/…`, excludes `__tests__/integration`) |
| `npm run test:integration` | Jest integration tests (`__tests__/integration/`) |
| `npm run test:e2e` | Playwright browser tests (`__tests__/e2e/`) — public flows and unauthenticated redirects |
| `npm run test:ci` | Same as `test:unit` (used in CI with coverage + JUnit reporter) |

## Testing layout

- **Unit** — Fast, isolated tests with mocks (e.g. `__tests__/lib/**`).
- **Integration** — Cross-module Jest suites in `__tests__/integration/`.
- **E2E** — Playwright specs in `__tests__/e2e/` (sign-in UI, navigation, optional backend health checks). Google OAuth is not automated; dashboard tests that require a real session are not included.

### Local Playwright

```bash
# Terminal 1
npm run dev

# Terminal 2
cd frontend && npm run test:e2e
```

In CI, Playwright starts the dev server with `CI=true` (see `playwright.config.ts`). To mirror that locally:

```bash
cd frontend && CI=1 npm run test:e2e
```

## GitHub Actions (frontend)

On push/PR to `development` and `production`, CI runs:

1. **Lint** — ESLint + TypeScript (`tsc --noEmit`).
2. In **parallel** (after lint): **unit** (Jest), **integration** (Jest), **E2E** (Playwright + Chromium).
3. **Build** — `npm run build` after all three test jobs succeed.

Backend jobs run in a separate workflow job (sequential Python steps). See `.github/workflows/ci.yml` at the repo root.

## Environment

Copy env from the root docs; for the app you typically need `frontend/.env` with `NEXTAUTH_*`, `NEXT_PUBLIC_API_URL`, and Google OAuth credentials for sign-in.
