# Rajniti — setup, up, dev-api, stop.
.PHONY: setup up dev-api stop

COMPOSE := docker compose --profile local-db
BUILD ?= 1

setup: ## Copy .env templates (safe to re-run)
	@test -f .env || cp .env.example .env
	@test -f frontend/.env || cp frontend/.env.example frontend/.env
	@echo "Env files ready. Edit .env and frontend/.env if needed, then: make up"

up: setup ## Start API :8000 + frontend :3000 + Postgres
	@if [ "$(BUILD)" = "1" ]; then \
		$(COMPOSE) up --build -d; \
	else \
		$(COMPOSE) up -d; \
	fi
	@echo "Rajniti is up — API http://localhost:8000  frontend http://localhost:3000"

dev-api: setup ## Start API :8000 + Postgres only
	@if [ "$(BUILD)" = "1" ]; then \
		$(COMPOSE) up --build -d postgres rajniti-api; \
	else \
		$(COMPOSE) up -d postgres rajniti-api; \
	fi
	@echo "Rajniti API is up — API http://localhost:8000"

stop: ## Stop containers
	$(COMPOSE) down
