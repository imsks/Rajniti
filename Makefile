# Makefile for Rajniti Election Data API
# Simple and easy to use

.PHONY: help default stop restart logs clean compile compile-python310 test test-unit test-integration test-e2e test-coverage test-ci lint format

default: ## Install, build, and start application (default command)
	@echo "🚀 Setting up and starting Rajniti..."
	@echo ""
	@echo "📥 Setting up virtual environment..."
	@python3 -m venv venv 2>/dev/null || true
	@. venv/bin/activate && pip install --upgrade pip pip-tools
	@echo "✅ Virtual environment ready"
	@echo ""
	@echo "📦 Compiling dependencies with pip-compile..."
	@PYTHON_VERSION=$$(. venv/bin/activate && python --version 2>&1 | cut -d' ' -f2); \
	PYTHON_MAJOR=$$(echo $$PYTHON_VERSION | cut -d'.' -f1); \
	PYTHON_MINOR=$$(echo $$PYTHON_VERSION | cut -d'.' -f2); \
	if [ -f requirements.txt ]; then \
		if [ "$$PYTHON_MAJOR" -gt 3 ] || ([ "$$PYTHON_MAJOR" -eq 3 ] && [ "$$PYTHON_MINOR" -ge 10 ]); then \
			echo "   Using Python $$PYTHON_VERSION (3.10+) - compiling fresh..."; \
			. venv/bin/activate && pip-compile requirements.in && echo "✅ Dependencies compiled successfully"; \
		else \
			echo "   Using Python $$PYTHON_VERSION (< 3.10) - using existing requirements.txt"; \
			echo "   (To compile fresh, use Python 3.10+ or run: make compile-python310)"; \
		fi; \
	else \
		echo "   No existing requirements.txt found - attempting compilation..."; \
		if . venv/bin/activate && pip-compile requirements.in 2>&1; then \
			echo "✅ Dependencies compiled successfully"; \
		else \
			echo "❌ Error: requirements.txt not found and compilation failed"; \
			echo "   Please use Python 3.10+ or provide an existing requirements.txt"; \
			exit 1; \
		fi; \
	fi
	@echo "✅ Dependencies ready"
	@echo ""
	@echo "📥 Installing dependencies..."
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Installation complete"
	@echo ""
	@echo "🔨 Building Docker image..."
	@docker-compose build
	@echo "✅ Build complete"
	@echo ""
	@echo "🚀 Starting application..."
	@docker-compose up -d
	@echo "✅ Application started at http://localhost:8000"

help: ## Show available commands
	@echo "Rajniti - Available Commands:"
	@echo ""
	@echo "  make                - Install, build, and start (all-in-one)"
	@echo "  make compile         - Compile requirements.txt (uses current Python)"
	@echo "  make compile-python310 - Compile using Python 3.10+ (recommended)"
	@echo "  make stop            - Stop application"
	@echo "  make restart         - Restart application"
	@echo "  make logs            - View logs"
	@echo "  make clean           - Clean up Docker resources"
	@echo ""

compile: ## Compile requirements.txt from requirements.in using pip-compile (uses current Python)
	@echo "📦 Compiling dependencies with pip-compile..."
	@python3 -m venv venv 2>/dev/null || true
	@. venv/bin/activate && pip install --upgrade pip pip-tools
	@PYTHON_VERSION=$$(. venv/bin/activate && python --version 2>&1 | cut -d' ' -f2); \
	echo "   Using Python $$PYTHON_VERSION"; \
	if . venv/bin/activate && pip-compile requirements.in; then \
		echo "✅ requirements.txt compiled from requirements.in"; \
	else \
		echo "❌ Compilation failed. Try using Python 3.10+:"; \
		echo "   python3.10 -m venv venv310 && . venv310/bin/activate && pip install pip-tools && pip-compile requirements.in"; \
		exit 1; \
	fi

compile-python310: ## Compile using Python 3.10+ (creates separate venv if needed)
	@echo "📦 Compiling dependencies with Python 3.10+..."
	@PYTHON310=$$(which python3.10 python3.11 python3.12 2>/dev/null | head -1); \
	if [ -z "$$PYTHON310" ]; then \
		echo "❌ Python 3.10+ not found. Install it with:"; \
		echo "   brew install python@3.10  # macOS"; \
		echo "   or download from https://www.python.org/downloads/"; \
		exit 1; \
	fi; \
	echo "   Using $$PYTHON310"; \
	$$PYTHON310 -m venv venv_compile 2>/dev/null || true; \
	. venv_compile/bin/activate && pip install --upgrade pip pip-tools && \
	pip-compile requirements.in && \
	echo "✅ requirements.txt compiled successfully" && \
	rm -rf venv_compile

stop: ## Stop application
	@echo "🛑 Stopping application..."
	@docker-compose down
	@echo "✅ Application stopped"

restart: ## Restart application
	@echo "🔄 Restarting application..."
	@docker-compose restart
	@echo "✅ Application restarted"

logs: ## View application logs
	@docker-compose logs -f

clean: ## Clean up Docker resources (containers, volumes, images)
	@echo "🧹 Cleaning up Docker resources..."
	@docker-compose down -v --rmi local
	@echo "✅ Cleanup complete"

# =============================================================================
# Testing Commands
# =============================================================================

test: ## Run all tests
	@echo "🧪 Running all tests..."
	@. venv/bin/activate && pytest tests/ -v
	@echo "✅ All tests completed"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@. venv/bin/activate && pytest tests/unit/ -v -m unit
	@echo "✅ Unit tests completed"

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@. venv/bin/activate && pytest tests/integration/ -v -m integration
	@echo "✅ Integration tests completed"

test-e2e: ## Run end-to-end tests only
	@echo "🧪 Running E2E tests..."
	@. venv/bin/activate && pytest tests/e2e/ -v -m e2e
	@echo "✅ E2E tests completed"

test-coverage: ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	@. venv/bin/activate && pytest tests/ -v \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-report=xml
	@echo "✅ Coverage report generated in htmlcov/"

test-ci: ## Run tests in CI mode (fast, with coverage)
	@echo "🧪 Running CI tests..."
	@. venv/bin/activate && pytest tests/ -v \
		--cov=app \
		--cov-report=xml \
		--cov-fail-under=60 \
		-n auto \
		--junitxml=test-results/junit.xml
	@echo "✅ CI tests completed"

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "🧪 Running tests in watch mode..."
	@. venv/bin/activate && ptw tests/

# =============================================================================
# Code Quality Commands
# =============================================================================

lint: ## Run linters (flake8, black check, isort check)
	@echo "🔍 Running linters..."
	@. venv/bin/activate && flake8 app/ tests/
	@. venv/bin/activate && black --check app/ tests/
	@. venv/bin/activate && isort --check-only app/ tests/
	@echo "✅ Linting completed"

format: ## Format code with black and isort
	@echo "🎨 Formatting code..."
	@. venv/bin/activate && black app/ tests/
	@. venv/bin/activate && isort app/ tests/
	@echo "✅ Code formatted"

security: ## Run security checks
	@echo "🔒 Running security checks..."
	@. venv/bin/activate && bandit -r app/ -ll
	@. venv/bin/activate && safety check -r requirements.txt || true
	@echo "✅ Security checks completed"

# =============================================================================
# Frontend Testing Commands
# =============================================================================

test-frontend: ## Run frontend tests
	@echo "🧪 Running frontend tests..."
	@cd frontend && npm run test
	@echo "✅ Frontend tests completed"

test-frontend-coverage: ## Run frontend tests with coverage
	@echo "🧪 Running frontend tests with coverage..."
	@cd frontend && npm run test:coverage
	@echo "✅ Frontend coverage report generated"

lint-frontend: ## Run frontend linting
	@echo "🔍 Running frontend linting..."
	@cd frontend && npm run lint
	@echo "✅ Frontend linting completed"

# =============================================================================
# Combined Commands
# =============================================================================

test-all: test test-frontend ## Run all backend and frontend tests
	@echo "✅ All tests completed"

lint-all: lint lint-frontend ## Run all linting checks
	@echo "✅ All linting completed"

ci-local: lint test-coverage ## Run full CI pipeline locally
	@echo "✅ Local CI completed"
