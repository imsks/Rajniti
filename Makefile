# Makefile for Rajniti Election Data API
# Simple and easy to use

.PHONY: help default stop restart logs clean compile compile-python310

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
