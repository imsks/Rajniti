# Multi-stage Dockerfile for Rajniti Election Data API
# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# ── Development (hot reload via volume mounts) ────────────────────────────────
FROM base AS development

ENV FLASK_ENV=development \
    FLASK_DEBUG=True

COPY app/ ./app/
COPY run.py .
COPY alembic.ini .
COPY alembic/ ./alembic/

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "run.py"]

# ── Production (Cloud Run / Supabase) ───────────────────────────────────────────
FROM base AS production

ENV FLASK_ENV=production \
    FLASK_DEBUG=False

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY app/ ./app/
COPY run.py .
COPY alembic.ini .
COPY alembic/ ./alembic/

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD exec gunicorn --bind :${PORT:-8000} --workers 1 --threads 8 --timeout 0 'app:create_app()'
