# Makefile for Rajniti Election Data API
# Usage: make <command> or make help

.PHONY: help setup dev test format lint clean install pre-commit \
	docker-up docker-down docker-build docker-logs docker-logs-api docker-logs-db docker-shell docker-restart docker-clean docker-ps \
	docker-up-prod docker-down-prod docker-build-prod docker-logs-prod docker-logs-api-prod docker-restart-prod docker-clean-prod docker-ps-prod \
	db-init db-sync db-reset db-migrate db-migrate-dry \
	agent-run vector-sync \
	scrape scrape-help

# ============================================================================
# Help & Documentation
# ============================================================================

help: ## Show this help message with all available commands
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║         Rajniti Election Data API - Makefile Commands         ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 Running the Application:"
	@echo ""
	@echo "  Normal App Running (without Docker):"
	@echo "    make setup          Set up the development environment"
	@echo "    make dev            Start the development server locally"
	@echo "    make install        Install/update Python dependencies"
	@echo ""
	@echo "  Docker Running:"
	@echo "    make docker-up      Start application with Docker"
	@echo ""
	@echo "📚 Other Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -vE '(setup|dev|install|docker-up|docker-down|docker-build|docker-logs|docker-shell|docker-restart|docker-clean|docker-ps|docker-up-prod|docker-down-prod|docker-build-prod|docker-logs-prod|docker-restart-prod|docker-clean-prod|docker-ps-prod)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "💡 Quick Start:"
	@echo "  Normal:  make setup && make dev"
	@echo "  Docker:  make docker-up"
	@echo ""

# ============================================================================
# Normal App Running (without Docker)
# ============================================================================

setup: ## Set up the development environment (creates venv, installs deps)
	@echo "🔧 Setting up development environment..."
	@if [ ! -f scripts/setup.sh ]; then \
		echo "⚠️  setup.sh not found. Creating virtual environment manually..."; \
		python3 -m venv venv; \
		. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt; \
	else \
		./scripts/setup.sh; \
	fi

dev: ## Start the development server locally (without Docker)
	@echo "🚀 Starting development server..."
	@if [ ! -f scripts/dev.sh ]; then \
		echo "⚠️  dev.sh not found. Running directly..."; \
		. venv/bin/activate && python run.py; \
	else \
		./scripts/dev.sh; \
	fi

install: ## Install/update Python dependencies
	@echo "📥 Installing dependencies..."
	@. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

# ============================================================================
# Docker Running
# ============================================================================

docker-up: ## Start application with Docker (uses DATABASE_URL from .env - Supabase or local postgres)
	@echo "🚀 Starting application with Docker..."
	@docker-compose up -d
	@echo "✅ Application started!"
	@echo "   📍 API: http://localhost:8000"
	@echo "   💡 Database: Using DATABASE_URL from .env"
	@echo "   💡 Use 'make docker-logs' to view logs"

docker-up-local-db: ## Start application with Docker + local PostgreSQL
	@echo "🚀 Starting application with Docker and local PostgreSQL..."
	@docker-compose --profile local-db up -d
	@echo "✅ Application started!"
	@echo "   📍 API: http://localhost:8000"
	@echo "   📍 PostgreSQL: localhost:5432"
	@echo "   💡 Use 'make docker-logs' to view logs"

docker-down: ## Stop Docker containers
	@echo "🛑 Stopping Docker containers..."
	@docker-compose down
	@echo "✅ Containers stopped"

docker-build: ## Build Docker image
	@echo "🔨 Building Docker image..."
	@docker-compose build
	@echo "✅ Build complete"

docker-logs: ## View container logs (follow mode)
	@echo "📋 Viewing container logs (Ctrl+C to exit)..."
	@docker-compose logs -f

docker-logs-api: ## View only API container logs (follow mode)
	@echo "📋 Viewing API container logs (Ctrl+C to exit)..."
	@docker-compose logs -f rajniti-api

docker-logs-db: ## View only PostgreSQL container logs (follow mode)
	@echo "📋 Viewing PostgreSQL container logs (Ctrl+C to exit)..."
	@docker-compose logs -f postgres

docker-shell: ## Open interactive shell in API container
	@echo "🐚 Opening shell in API container..."
	@docker-compose exec rajniti-api /bin/bash

docker-restart: ## Restart all containers
	@echo "🔄 Restarting containers..."
	@docker-compose restart
	@echo "✅ Containers restarted"

docker-clean: ## Stop and remove containers, volumes, and images (WARNING: deletes data)
	@echo "🧹 Cleaning up Docker resources..."
	@echo "⚠️  WARNING: This will delete all containers, volumes, and images!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi local; \
		echo "✅ Cleanup complete"; \
	else \
		echo "❌ Cleanup cancelled"; \
	fi

docker-ps: ## Show status of containers
	@echo "📊 Container status:"
	@docker-compose ps

# Production Docker commands (available but not shown in help)
docker-up-prod: ## Start production containers (GCP-ready, no hot reload)
	@echo "🚀 Starting production containers..."
	@docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Production containers started!"
	@echo "   📍 API: http://localhost:8000"
	@echo "   💡 Use 'make docker-logs-prod' to view logs"

docker-down-prod: ## Stop production containers
	@echo "🚀 Stopping production containers..."
	@docker-compose -f docker-compose.prod.yml down
	@echo "✅ Production containers stopped"

docker-build-prod: ## Build production Docker image (optimized for GCP)
	@echo "🚀 Building production Docker image..."
	@docker-compose -f docker-compose.prod.yml build
	@echo "✅ Production build complete"

docker-logs-prod: ## View all production container logs (follow mode)
	@echo "📋 Viewing production container logs (Ctrl+C to exit)..."
	@docker-compose -f docker-compose.prod.yml logs -f

docker-logs-api-prod: ## View only production API container logs (follow mode)
	@echo "📋 Viewing production API container logs (Ctrl+C to exit)..."
	@docker-compose -f docker-compose.prod.yml logs -f rajniti-api

docker-restart-prod: ## Restart all production containers
	@echo "🔄 Restarting production containers..."
	@docker-compose -f docker-compose.prod.yml restart
	@echo "✅ Production containers restarted"

docker-clean-prod: ## Stop and remove production containers, volumes, and images (WARNING: deletes data)
	@echo "🧹 Cleaning up production Docker resources..."
	@echo "⚠️  WARNING: This will delete all production containers, volumes, and images!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f docker-compose.prod.yml down -v --rmi local; \
		echo "✅ Production cleanup complete"; \
	else \
		echo "❌ Cleanup cancelled"; \
	fi

docker-ps-prod: ## Show status of production containers
	@echo "📊 Production container status:"
	@docker-compose -f docker-compose.prod.yml ps

# ============================================================================
# Development Commands
# ============================================================================

test: ## Run all tests
	@echo "🧪 Running tests..."
	@if [ ! -f scripts/test.sh ]; then \
		echo "⚠️  test.sh not found. Running pytest directly..."; \
		. venv/bin/activate && pytest tests/ -v; \
	else \
		./scripts/test.sh; \
	fi

format: ## Format code with autoflake, black, and isort
	@echo "✨ Formatting code..."
	@if [ ! -f scripts/format.sh ]; then \
		echo "⚠️  format.sh not found. Running formatters directly..."; \
		. venv/bin/activate && \
		autoflake --in-place --remove-all-unused-imports --recursive app/ && \
		black app/ && \
		isort app/; \
	else \
		./scripts/format.sh; \
	fi

lint: ## Run linting checks (flake8, black, isort)
	@echo "🔍 Running linting checks..."
	@. venv/bin/activate && flake8 app/ || true
	@. venv/bin/activate && black --check app/ || true
	@. venv/bin/activate && isort --check-only app/ || true

pre-commit: ## Install pre-commit hooks for code quality
	@echo "🔗 Installing pre-commit hooks..."
	@. venv/bin/activate && pre-commit install

clean: ## Clean up temporary files (pyc, __pycache__, etc.)
	@echo "🧹 Cleaning up temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete
	@echo "✅ Cleanup complete"

# ============================================================================
# Database Commands
# ============================================================================

db-init: ## Initialize database (create all tables)
	@echo "🗄️  Initializing database..."
	@. venv/bin/activate && python scripts/db.py init
	@echo "✅ Database initialized"

db-sync: ## Sync database with models (auto-generate and run migrations)
	@echo "🔄 Syncing database with models..."
	@. venv/bin/activate && python scripts/db.py sync
	@echo "✅ Database sync complete"

db-reset: ## Reset database (WARNING: drops all tables and recreates them)
	@echo "⚠️  WARNING: This will delete all data in the database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		. venv/bin/activate && python scripts/db.py reset; \
		echo "✅ Database reset complete"; \
	else \
		echo "❌ Database reset cancelled"; \
	fi

db-migrate: ## Migrate JSON election data to database
	@echo "📦 Migrating JSON election data to database..."
	@. venv/bin/activate && python scripts/db.py migrate
	@echo "✅ Migration complete"

db-migrate-dry: ## Preview JSON migration without making changes
	@echo "👀 Previewing JSON migration (dry run)..."
	@. venv/bin/activate && python scripts/db.py migrate --dry-run
	@echo "✅ Dry run complete"

# ============================================================================
# AI Agent Commands
# ============================================================================

agent-run: ## Run candidate data population agent
	@echo "🤖 Running candidate data population agent..."
	@. venv/bin/activate && python scripts/run_candidate_agent.py
	@echo "✅ Agent run complete"

vector-sync: ## Sync candidates to vector database (ChromaDB)
	@echo "🔗 Syncing candidates to vector database..."
	@. venv/bin/activate && python scripts/sync_candidates_to_vector_db.py
	@echo "✅ Vector sync complete"

# ============================================================================
# Scraping Commands
# ============================================================================

scrape: ## Run election data scraping
	@echo "🕸️  Starting election data scraping..."
	@. venv/bin/activate && python scripts/scrape_elections.py 2>/dev/null || \
		echo "⚠️  scrape_elections.py not found. Check scripts directory."

scrape-help: ## Show scraping help and available tools
	@echo "🕸️  Election Data Scraping Commands:"
	@echo ""
	@echo "  make scrape        - Run the main scraping script"
	@echo "  python scripts/scrape_elections.py - Run scraping directly"
	@echo ""
	@echo "📚 Available scraping tools:"
	@echo "  - requests: HTTP requests"
	@echo "  - beautifulsoup4: HTML parsing"
	@echo "  - httpx: Async HTTP requests"
	@echo ""
	@echo "💡 For more information, check the scripts/ directory"
