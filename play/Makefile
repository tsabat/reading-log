.PHONY: install init-db run clean test help check-port kill-port start-all frontend install-frontend install-all build-frontend

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON = poetry run python
PORT ?= 8888
HOST = 0.0.0.0
FRONTEND_PORT ?= 5173

help:
	@echo "Reading Tracker API - Makefile Commands"
	@echo "--------------------------------------"
	@echo "make install              - Install backend dependencies using Poetry"
	@echo "make install-frontend     - Install frontend dependencies using npm"
	@echo "make install-all          - Install both backend and frontend dependencies"
	@echo "make init-db              - Initialize the database"
	@echo "make run                  - Run the backend on port $(PORT)"
	@echo "make run PORT=3000        - Run the backend on a specific port"
	@echo "make frontend             - Run the frontend development server"
	@echo "make start-all            - Run both backend and frontend"
	@echo "make build-frontend       - Build the frontend for production"
	@echo "make clean                - Remove database and cache files"
	@echo "make test                 - Run tests"
	@echo "make check-port           - Check if port $(PORT) is in use"
	@echo "make kill-port            - Kill process using port $(PORT)"

install:
	@echo "Installing backend dependencies..."
	poetry install

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

install-all: install install-frontend
	@echo "All dependencies installed successfully!"

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
	@echo "Cleaning frontend build files..."
	rm -rf frontend/.svelte-kit
	rm -rf frontend/build

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest

frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

build-frontend:
	@echo "Building frontend for production..."
	cd frontend && npm run build
	@echo "Frontend built successfully! Output is in frontend/build"

# Run both backend and frontend
start-all: init-db
	@echo "Starting both backend and frontend..."
	@echo "Backend will be available at http://$(HOST):$(PORT)"
	@echo "Frontend will be available at http://localhost:$(FRONTEND_PORT)"
	@trap 'kill $${BACKEND_PID} $${FRONTEND_PID}; exit 0' INT TERM
	@$(PYTHON) -m uvicorn app.main:app --host $(HOST) --port $(PORT) --reload & export BACKEND_PID=$$!; \
	cd frontend && npm run dev & export FRONTEND_PID=$$!; \
	wait
