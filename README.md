# Reading Tracker API

A simple FastAPI application to track reading sessions using SQLObject as the ORM.

## Features

- Track reading sessions with date and duration
- RESTful API built with FastAPI
- SQLObject for database operations

## Setup

### Using Makefile (Recommended)

The project includes a Makefile to simplify common tasks:

```bash
# Install dependencies
make install

# Initialize the database
make init-db

# Check if the default port (8888) is in use
make check-port

# Kill any process using the default port
make kill-port

# Run the application on the default port (8888)
make run

# Run the application on a specific port
make run PORT=3000

# Clean up database and cache files
make clean

# Run tests
make test

# Show available commands
make help
```

### Manual Setup

1. Install dependencies using Poetry:

```bash
poetry install
```

2. Run the application (this will initialize the database automatically):

```bash
poetry run python run.py
```

Alternatively, you can initialize the database and run the application separately:

```bash
# Initialize the database
poetry run python -m app.db.init_db

# Run the application
poetry run uvicorn app.main:app --reload --port 8888
```

3. Access the API documentation at http://localhost:8888/docs (or the port you specified)

## API Endpoints

- `GET /sessions`: List all reading sessions
- `POST /sessions`: Create a new reading session
- `GET /sessions/{session_id}`: Get a specific reading session
- `PUT /sessions/{session_id}`: Update a reading session
- `DELETE /sessions/{session_id}`: Delete a reading session

## Troubleshooting

If you encounter database errors:

1. Make sure the `data` directory exists in the project root
2. Check that your user has write permissions to the project directory
3. Try running the application with the run script: `poetry run python run.py`
4. Use `make clean` to remove any corrupted database files, then `make run` to start fresh

If you encounter "Address already in use" errors:

1. Check which process is using the port: `make check-port`
2. Try running on a different port: `make run PORT=3000`
3. Note: Port 5000 is commonly used by macOS Control Center and other system services
