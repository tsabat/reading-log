# Reading App

A simple application for tracking reading activities.

## Features

- Track reading logs with duration and description
- CRUD operations for managing reading logs
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
- `make debug-port` - Run a simple HTTP server to debug port forwarding
- `make check-port` - Check if the port is accessible

### Scripts

The project includes several utility scripts in the `scripts/` directory:

- `scripts/init_db.py` - Initialize the database
- `scripts/migrate_db.py` - Run database migrations
- `scripts/run_app.py` - Run the application
- `scripts/debug_port.py` - Debug port forwarding issues

### API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8888/docs
- ReDoc: http://localhost:8888/redoc

## API Endpoints

### Reading Logs API

- `GET /reading-logs` - Get all reading logs
- `POST /reading-logs` - Create a new reading log
- `GET /reading-logs/{reading_log_id}` - Get a specific reading log
- `PATCH /reading-logs/{reading_log_id}` - Update a reading log
- `DELETE /reading-logs/{reading_log_id}` - Delete a reading log

## Deployment

### Railway

This application is configured for deployment on Railway using Docker containers.

#### Prerequisites

- [Railway CLI](https://docs.railway.app/develop/cli) (optional, but recommended)
- A Railway account
- A GitHub repository with your code

#### Deployment Steps

1. Push your code to a GitHub repository:

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

2. Create a new project on Railway:
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository
   - Click "Deploy Now"

3. Add a PostgreSQL database:
   - In your project dashboard, click "New"
   - Select "Database" and then "PostgreSQL"
   - Railway will automatically create a PostgreSQL database and provide the connection details

4. Link the database to your application:
   - In your project dashboard, click on your application service
   - Go to the "Variables" tab
   - Railway will automatically add the `DATABASE_URL` variable from your PostgreSQL service
   - Add additional environment variables if needed:
     - `ENVIRONMENT=production`

5. Your application will automatically deploy and be accessible at the provided Railway URL.

#### Using Railway CLI (Optional)

If you prefer using the CLI:

```bash
# Login to Railway
railway login

# Link to your project
railway link

# Add PostgreSQL plugin
railway add

# Deploy your application
railway up
```

## Development

### Database

- In local development, the application uses SQLite by default
- In production, it uses PostgreSQL

The application automatically detects which database to use based on the presence of the `DATABASE_URL` environment variable.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
