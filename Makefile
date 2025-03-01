.PHONY: install run dev clean test lint format docker-build docker-run help db-init db-migrate export-requirements setup check-port debug-port test-api

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON = python
POETRY = poetry
DOCKER = docker
APP_NAME = reading-app
PORT = 8888
HOST = 0.0.0.0
API_URL = https://web-production-f727e.up.railway.app

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	$(POETRY) install

run: ## Run the application in production mode
	$(POETRY) run $(PYTHON) scripts/run_app.py

dev: ## Run the application in development mode with auto-reload
	$(POETRY) run uvicorn app.main:app --reload --host $(HOST) --port $(PORT)

clean: ## Remove SQLite database and cache files
	rm -f *.db
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +

test: ## Run tests
	$(POETRY) run pytest

lint: ## Run linters
	$(POETRY) run ruff check .
	$(POETRY) run mypy .

format: ## Format code
	$(POETRY) run ruff format .

docker-build: ## Build Docker image
	$(DOCKER) build -t $(APP_NAME) .

docker-run: ## Run Docker container
	$(DOCKER) run -p $(PORT):$(PORT) --name $(APP_NAME) -e PORT=$(PORT) $(APP_NAME)

db-init: ## Initialize the database
	$(POETRY) run $(PYTHON) scripts/init_db.py

db-migrate: ## Run database migrations
	$(POETRY) run $(PYTHON) scripts/migrate_db.py

export-requirements: ## Export requirements.txt for non-Poetry environments
	$(POETRY) export -f requirements.txt --output requirements.txt --without-hashes

setup: install db-init ## Setup the project (install dependencies and initialize database)

check-port: ## Check if the port is accessible
	@echo "Checking if port $(PORT) is accessible..."
	@nc -z localhost $(PORT) && echo "Port $(PORT) is open and accessible!" || echo "Port $(PORT) is not accessible."

debug-port: ## Run a simple HTTP server to debug port forwarding
	$(POETRY) run $(PYTHON) scripts/debug_port.py

test-api: ## Test the API endpoints
	$(POETRY) run $(PYTHON) scripts/test_api.py --url $(API_URL)
