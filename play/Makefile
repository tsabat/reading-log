.PHONY: install init-db run clean test help check-port kill-port

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON = poetry run python
PORT ?= 8888
HOST = 0.0.0.0

help:
	@echo "Reading Tracker API - Makefile Commands"
	@echo "--------------------------------------"
	@echo "make install              - Install dependencies using Poetry"
	@echo "make init-db              - Initialize the database"
	@echo "make run                  - Run the application on port $(PORT)"
	@echo "make run PORT=3000        - Run the application on a specific port"
	@echo "make clean                - Remove database and cache files"
	@echo "make test                 - Run tests"
	@echo "make check-port           - Check if port $(PORT) is in use"
	@echo "make kill-port            - Kill process using port $(PORT)"

install:
	@echo "Installing dependencies..."
	poetry install

init-db:
	@echo "Initializing database..."
	$(PYTHON) -m app.db.init_db

check-port:
	@echo "Checking if port $(PORT) is in use..."
	@lsof -i :$(PORT) || echo "Port $(PORT) is available"

kill-port:
	@echo "Attempting to kill process using port $(PORT)..."
	@lsof -ti :$(PORT) | xargs kill -9 || echo "No process found on port $(PORT)"

run: init-db
	@echo "Starting application on http://$(HOST):$(PORT)"
	$(PYTHON) -m uvicorn app.main:app --host $(HOST) --port $(PORT) --reload

clean:
	@echo "Cleaning up..."
	rm -rf data/*.db
	rm -rf __pycache__
	rm -rf app/__pycache__
	rm -rf app/*/__pycache__
	rm -rf .pytest_cache

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest
