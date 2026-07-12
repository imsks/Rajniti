# Cloud Run image for the Rajniti Flask backend.
# Optimized for fast cold starts + small image: multi-stage uv build, slim base,
# non-root user, bytecode-compiled deps. The prebuilt Chroma index is baked in
# under /app/index (populated by the ingestion pipeline at build time).

# ---- builder ---------------------------------------------------------------
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Install deps first (cached layer), then the project.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---- runtime ---------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Non-root user.
RUN groupadd --system app && useradd --system --gid app --create-home app

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

COPY --from=builder --chown=app:app /app /app

USER app
EXPOSE 8080

# gunicorn: threaded workers suit request-scoped agent work while keeping the
# instance able to scale to zero. Tune workers/threads via env if needed.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers ${WEB_CONCURRENCY:-2} --threads ${WEB_THREADS:-4} --timeout 120 'app:create_app()'"]
