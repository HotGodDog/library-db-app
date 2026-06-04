.PHONY: install install-dev install-prod run test coverage lint clean clean-cache reset-db reset help docker-build docker-up docker-down

# Python

ifeq ($(OS),Windows_NT)
    PYTHON := python
    PIP := python -m pip
else
    PYTHON := python3
    PIP := python3 -m pip
endif

# Install

install-prod:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -e ".[dev]"

install:
	$(PIP) install -r requirements.lock

# Run

run:
	$(PYTHON) -m flask --app src/app run --debug

# Test

test: clean-cache
	$(PYTHON) -m pytest tests/ -v --tb=short

coverage: clean-cache
	$(PYTHON) -m pytest tests/ --cov=src/app --cov-report=html --cov-report=term -v

# Lint

lint:
	$(PYTHON) -m ruff check src/ tests/

# Clean

clean-cache:
	@echo "Cleaning cache..."
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .coverage htmlcov/

clean: clean-cache
	@rm -rf build/ dist/ *.egg-info/

# Database

reset-db:
	rm -f library.db

reset: clean reset-db
	@echo "Project reset. Run 'make run' to create new database."

# --- Docker ---

docker-build:
	docker build -t library-db-app:latest .

docker-up:
	docker compose -f infra/compose.yaml up --build -d

# Data-saving stop
docker-stop:
	docker compose -f infra/compose.yaml down

# Complete cleaning with data deletion
docker-down:
	docker compose -f infra/compose.yaml down -v

docker-logs:
	docker compose -f infra/compose.yaml logs -f || true

docker-shell:
	docker compose -f infra/compose.yaml exec app /bin/sh

# Help

help:
	@echo "Available commands:"
	@echo "  make install-prod    - Install from requirements.txt (TestPyPI)"
	@echo "  make install-dev     - Install editable with dev deps"
	@echo "  make install         - Install from requirements.lock"
	@echo "  make run             - Run application locally"
	@echo "  make test            - Run tests"
	@echo "  make coverage        - Run tests with coverage report"
	@echo "  make lint            - Run linter"
	@echo "  make docker-build    - Build Docker image"
	@echo "  make docker-up       - Start Docker Compose"
	@echo "  make docker-stop     - Stop Compose (preserve data)"
	@echo "  make docker-down     - Stop Compose and remove volume"
	@echo "  make docker-logs     - View container logs"
	@echo "  make docker-shell    - Open shell in container"
	@echo "  make reset-db        - Delete database file"
	@echo "  make reset           - Full project reset"
	@echo "  make clean           - Clean cache and artifacts"
	@echo "  make help            - This help"