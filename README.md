# Reading App

A simple application for tracking reading sessions.

## Features

- Track reading sessions with duration and description
- CRUD operations for managing reading sessions
- API built with FastAPI and SQLModel
- Support for both SQLite (local development) and PostgreSQL (production)

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- Make (optional, but recommended)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/reading-app.git
cd reading-app
```

2. Install dependencies:

```bash
# Using Make
make install

# Or using Poetry directly
poetry install
```

3. Create a `.env` file (or use the existing one) and configure your environment variables:

```
# Database configuration
# Uncomment and set DATABASE_URL for PostgreSQL in production
# DATABASE_URL=postgresql://user:password@localhost:5432/reading_app

# API configuration
API_HOST=0.0.0.0
API_PORT=8888
```

4. Initialize the database:

```bash
# Using Make
make db-init

# Or using the script directly
poetry run python scripts/init_db.py
```

### Running the Application

Run the application locally:

```bash
# Using Make
make run  # Production mode
make dev  # Development mode with auto-reload

# Or using the scripts directly
poetry run python scripts/run_app.py
# or
poetry run python run.py
```

The API will be available at http://localhost:8888.

### Available Make Commands

The project includes a Makefile with various commands to simplify development:

- `make help` - Show available commands
- `make install` - Install dependencies
- `make run` - Run the application in production mode
- `make dev` - Run the application in development mode with auto-reload
- `make clean` - Remove SQLite database and cache files
- `make test` - Run tests
- `make lint` - Run linters
- `make format` - Format code
- `make docker-build` - Build Docker image
- `make docker-run` - Run Docker container
- `make db-init` - Initialize the database
- `make db-migrate` - Run database migrations
- `make export-requirements` - Export requirements.txt for non-Poetry environments
- `make setup` - Setup the project (install dependencies and initialize database)

### Scripts

The project includes several utility scripts in the `scripts/` directory:

- `scripts/init_db.py` - Initialize the database
- `scripts/migrate_db.py` - Run database migrations
- `scripts/run_app.py` - Run the application

### API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8888/docs
- ReDoc: http://localhost:8888/redoc

## API Endpoints

- `GET /sessions` - Get all reading sessions
- `POST /sessions` - Create a new reading session
- `GET /sessions/{session_id}` - Get a specific reading session
- `PATCH /sessions/{session_id}` - Update a reading session
- `DELETE /sessions/{session_id}` - Delete a reading session

## Deployment

### Railway

This application is configured for deployment on Railway using Docker containers.

1. Push your code to a GitHub repository
2. Create a new project on Railway from your GitHub repository
3. Railway will automatically detect the Dockerfile and build your application
4. Set the required environment variables in the Railway dashboard:
   - `DATABASE_URL` - PostgreSQL connection string (Railway will provide this automatically if you add a PostgreSQL plugin)

## Development

### Database

- In local development, the application uses SQLite by default
- In production, it uses PostgreSQL

The application automatically detects which database to use based on the presence of the `DATABASE_URL` environment variable.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
