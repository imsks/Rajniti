# Rajniti Makefile
.PHONY: help dev stop test

VENV := . venv/bin/activate &&

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ── Run (Docker) ──────────────────────────────────────────────────────────────

dev: ## Start backend + frontend + Postgres (Docker)
	docker compose --profile local-db up --build

stop: ## Stop all Docker containers
	docker compose --profile local-db down

# ── Test ──────────────────────────────────────────────────────────────────────

install-hooks: ## Install git pre-commit hook (auto-stamps lastUpdated on politician data changes)
	@printf '#!/bin/sh\npython3 "%s/scripts/pre_commit_hook.py"\n' "$$(git rev-parse --show-toplevel)" > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Pre-commit hook installed."

test: ## Run backend + frontend unit tests
	$(VENV) pytest tests/unit -v
	cd frontend && npm test -- --passWithNoTests
