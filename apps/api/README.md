# @rajniti/api

Rajniti backend — a **Flask modular monolith**. Deploys to **GCP Cloud Run** as
a container. Python deps are managed by [`uv`](https://docs.astral.sh/uv/); the
`package.json` is only a Turborepo task shim.

## Modules

A modular monolith with strict internal boundaries. Each module exposes a
public **facade** (re-exported from its `__init__.py`) and crosses boundaries
using plain **DTOs** — never ORM rows or Chroma handles.

```
app/
  core/       shared infra (config, logging, exceptions) — unrestricted
  promises/   promises made vs kept
  reps/       representatives / politicians
  rag/        retrieval over the embedded Chroma index
  agents/     LangGraph agents (request-scoped execution)
```

Allowed dependency direction (enforced by `import-linter` in CI):

```
(promises, reps)  ->  rag  ->  agents
```

Siblings on the same layer (`promises`, `reps`) may not import each other.

## Local development

```bash
uv sync --all-groups          # or: pnpm --filter @rajniti/api setup
pnpm dev:api                  # from repo root (Flask on :8000)
```

## Checks

```bash
pnpm --filter @rajniti/api lint        # ruff + import-linter (boundaries)
pnpm --filter @rajniti/api typecheck   # pyright
pnpm --filter @rajniti/api test        # pytest (colocated unit + tests/ integration)
```

## Container

```bash
uv lock                                # keep uv.lock current
pnpm --filter @rajniti/api build       # docker build (Cloud Run image)
```

The prebuilt Chroma index is baked into the image at `/app/index` by the
ingestion pipeline at build time.
