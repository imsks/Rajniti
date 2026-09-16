# Rajniti Makefile
.PHONY: help setup install install-dev install-hooks run dev dev-api dev-build stop prod \
	test lint format db-migrate db-reset frontend-install frontend-dev logs

VENV := . venv/bin/activate &&
PYTHON ?= python3
SUITE ?= all
COV ?=
BUILD ?= 1
COMPOSE := docker compose --profile local-db

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── First-time setup ────────────────────────────────────────────────────────────

setup: ## Copy .env templates (safe to re-run)
	@test -f .env || cp .env.example .env
	@test -f frontend/.env || cp frontend/.env.example frontend/.env
	@echo "Env files ready. Edit .env (DATABASE_URL, optional LLM keys) and frontend/.env (NEXTAUTH_*)."

install: ## Create venv and install Python deps
	$(PYTHON) -m venv venv
	$(VENV) pip install -U pip && pip install -r requirements.txt

install-dev: install ## + test/lint deps (requirements-test.txt)
	$(VENV) pip install -r requirements-test.txt

install-hooks: ## Git pre-commit hook (auto-stamps lastUpdated on politician data changes)
	@printf '#!/bin/sh\npython3 "%s/scripts/pre_commit_hook.py"\n' "$$(git rev-parse --show-toplevel)" > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Pre-commit hook installed."

# ── Local (no Docker) ─────────────────────────────────────────────────────────

run: ## Local Flask API on :8000 (requires venv + Postgres)
	$(VENV) python run.py

frontend-install: ## npm ci in frontend/
	cd frontend && npm ci

frontend-dev: ## Local Next.js dev server on :3000
	cd frontend && npm run dev

# ── Docker ────────────────────────────────────────────────────────────────────

dev: setup ## Docker: API + frontend + Postgres (full stack)
	@if [ "$(BUILD)" = "1" ]; then \
		$(COMPOSE) up --build; \
	else \
		$(COMPOSE) up; \
	fi

dev-api: setup ## Docker: API + Postgres only (fastest — skip frontend image)
	@if [ "$(BUILD)" = "1" ]; then \
		$(COMPOSE) up --build postgres rajniti-api; \
	else \
		$(COMPOSE) up postgres rajniti-api; \
	fi

dev-build: ## Rebuild Docker images without starting containers
	$(COMPOSE) build

stop: ## Stop Docker containers
	$(COMPOSE) down

logs: ## Tail Docker logs (SERVICE=rajniti-api|rajniti-web|postgres)
	$(COMPOSE) logs -f $(SERVICE)

prod: ## Docker prod API (Supabase DATABASE_URL in .env)
	docker compose -f docker-compose.prod.yml up --build

# ── Database ──────────────────────────────────────────────────────────────────

db-migrate: ## Run Alembic migrations (local venv)
	$(VENV) python scripts/db.py migrate

db-reset: ## Stop Docker and delete Postgres volume (destroys local DB data)
	$(COMPOSE) down -v
	@echo "Local Postgres volume removed."

# ── Test & quality ────────────────────────────────────────────────────────────

test: ## Run tests (SUITE=unit|integration|e2e|all, COV=1 for coverage)
	@if [ "$(SUITE)" = "unit" ]; then \
		$(VENV) pytest tests/unit -v $(if $(COV),--cov=app --cov-report=term-missing,); \
	elif [ "$(SUITE)" = "integration" ]; then \
		$(VENV) pytest tests/integration -v; \
	elif [ "$(SUITE)" = "e2e" ]; then \
		$(VENV) pytest tests/e2e -v; \
	else \
		$(VENV) pytest tests/unit tests/integration tests/e2e -v $(if $(COV),--cov=app --cov-report=term-missing,); \
		cd frontend && npm test -- --passWithNoTests; \
	fi

lint: ## black + isort + flake8 + mypy + frontend eslint
	$(VENV) black --check app tests scripts
	$(VENV) isort --check-only app tests scripts
	$(VENV) flake8 app tests scripts
	$(VENV) mypy app
	cd frontend && npm run lint && npx tsc --noEmit

format: ## Auto-format Python (black + isort)
	$(VENV) black app tests scripts
	$(VENV) isort app tests scripts
