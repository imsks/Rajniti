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

- **Unit** — Fast, isolated tests with mocks (`__tests__/lib/**`, `__tests__/hooks/**`). Example: `usePoliticians` (load, filters, stats, refetch).
- **Integration** — Cross-hook checks in `__tests__/integration/` (e.g. `dashboard-search-and-data.test.ts` for list + debounced search).
- **E2E** — Playwright in `__tests__/e2e/`: `auth.spec.ts` (sign-in UI, optional API health), `dashboard.spec.ts` (protected-route redirects, home hero). Google OAuth is not automated; the full logged-in dashboard UI is not covered in E2E.

### Local Playwright

Only one `next dev` can run per app (Next.js lock under `.next/dev`). Playwright is configured to **reuse** whatever is already on port 3000, so you can keep `npm run dev` running and run tests in another terminal:

```bash
# Terminal 1
npm run dev

# Terminal 2
cd frontend && npm run test:e2e
```

If you see “Unable to acquire lock”, stop other `next dev` processes or remove a stale lock: `rm -rf .next/dev`.

If you already have a dev server running on a different port, skip Playwright's webServer and point to it explicitly:

```bash
PLAYWRIGHT_BASE_URL=http://127.0.0.1:3001 PLAYWRIGHT_SKIP_WEB_SERVER=true npm run test:e2e
```

With no dev server running, Playwright starts one for you. To mirror CI (cold start):

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
