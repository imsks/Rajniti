# @rajniti/web

Next.js (App Router, TypeScript) frontend for Rajniti. Deploys to **Vercel**.

> Shell placeholder. The existing `frontend/` is relocated here during the
> migration step (see the repo root plan / `CONTRIBUTING.md`). Until then the
> scripts are no-ops so the Turborepo graph stays green.

## UI primitives

This app consumes [`@sutra/ui`](https://www.npmjs.com/package/@sutra/ui) as a
public npm dependency. Do **not** build or vendor UI primitives here — install
`@sutra/ui` once it is published and compose from it.

## Local development

From the repo root:

```bash
pnpm install
pnpm dev            # starts infra + web + api
pnpm dev:web        # just this app
```

## Environment

```bash
cp .env.example .env.local
```

Production env vars are managed in the Vercel dashboard (per-environment).
