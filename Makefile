# Rajniti Makefile
.PHONY: help dev prod run stop logs clean test test-unit test-e2e coverage lint format db-init db-migrate db-reset frontend

# ═══════════════════════════════════════════════════════════════════════════════
# DEVELOPMENT
# ═══════════════════════════════════════════════════════════════════════════════

help: ## Show commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

dev: ## Start with local Postgres (Docker)
	docker compose --profile local-db up --build

prod: ## Start with Supabase (Docker)
	docker compose -f docker-compose.prod.yml up --build

run: ## Run local Python server
	. venv/bin/activate && python run.py

stop: ## Stop all containers
	docker compose --profile local-db down
	docker compose -f docker-compose.prod.yml down 2>/dev/null || true

logs: ## Tail API logs
	docker compose logs -f rajniti-api

clean: ## Remove containers + volumes
	docker compose --profile local-db down -v --rmi local 2>/dev/null || true
	docker compose -f docker-compose.prod.yml down -v --rmi local 2>/dev/null || true

# ═══════════════════════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════════════════════

test: ## Run all tests
	. venv/bin/activate && pytest tests/ -v

test-unit: ## Run unit tests
	. venv/bin/activate && pytest tests/unit/ -v

test-e2e: ## Run E2E tests
	. venv/bin/activate && pytest tests/e2e/ -v

coverage: ## Run tests with coverage
	. venv/bin/activate && pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

lint: ## Run linters
	. venv/bin/activate && flake8 app/ tests/ && black --check app/ tests/

format: ## Format code
	. venv/bin/activate && black app/ tests/ && isort app/ tests/

# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

db-init: ## Initialize tables
	. venv/bin/activate && python scripts/db.py init

db-migrate: ## Run migrations
	. venv/bin/activate && python scripts/db.py migrate

db-reset: ## Reset database (⚠️ deletes data)
	. venv/bin/activate && python scripts/db.py reset

db-shell: ## Open psql shell
	docker exec -it rajniti-postgres psql -U rajniti rajniti

# ═══════════════════════════════════════════════════════════════════════════════
# FRONTEND
# ═══════════════════════════════════════════════════════════════════════════════

frontend: ## Start frontend dev server
	cd frontend && npm run dev

frontend-test: ## Run frontend tests
	cd frontend && npm test

frontend-lint: ## Lint frontend
	cd frontend && npm run lint

# ═══════════════════════════════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════════════════════════════

install: ## Install dependencies
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

install-dev: ## Install with dev dependencies
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt -r requirements-test.txt
