# Rajniti — setup, up, stop.
.PHONY: setup up stop

COMPOSE := docker compose --profile local-db

setup: ## Copy .env templates (safe to re-run)
	@test -f .env || cp .env.example .env
	@test -f frontend/.env || cp frontend/.env.example frontend/.env
	@echo "Env files ready. Edit .env and frontend/.env if needed, then: make up"

up: setup ## Start API :8000 + frontend :3000 + Postgres
	$(COMPOSE) up --build -d
	@echo "Rajniti is up — API http://localhost:8000  frontend http://localhost:3000"

stop: ## Stop containers
	$(COMPOSE) down
