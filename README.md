# Reading Tracker

A full-stack application for tracking your reading sessions, built with FastAPI and SvelteKit.

## Features

- Track reading sessions with date and duration
- View all your reading sessions
- Edit or delete existing sessions
- See statistics about your total reading time

## Tech Stack

### Backend
- FastAPI
- SQLObject (ORM)
- Uvicorn (ASGI server)
- Poetry (dependency management)

### Frontend
- SvelteKit
- TypeScript
- Vite

## Getting Started

### Prerequisites

- Python 3.8+
- Poetry (Python package manager)
- Node.js (v16+)
- npm or yarn

### Installation

Clone the repository and navigate to the project directory:

```bash
git clone <repository-url>
cd <repository-directory>
```

#### Using Make (Recommended)

The project includes a Makefile with various commands to simplify development:

1. Install all dependencies (backend and frontend):
   ```bash
   make install-all
   ```

2. Initialize the database:
   ```bash
   make init-db
   ```

3. Start both backend and frontend servers:
   ```bash
   make start-all
   ```

#### Manual Installation

1. Install backend dependencies:
   ```bash
   poetry install
   ```

2. Install frontend dependencies:
   ```bash
   cd play/frontend
   npm install
   ```

### Running the Application

#### Using Make

- Run both backend and frontend:
  ```bash
  make start-all
  ```

- Run only the backend:
  ```bash
  make run
  ```

- Run only the frontend:
  ```bash
  make frontend
  ```

#### Manual Running

1. Run the backend:
   ```bash
   cd play
   python run.py
   ```

2. Run the frontend:
   ```bash
   cd play/frontend
   npm run dev
   ```

## Development

### Building for Production

Build the frontend for production:
```bash
make build-frontend
```

### Cleaning Up

Clean database and build files:
```bash
make clean
```

## API Endpoints

- `GET /sessions` - Get all reading sessions
- `POST /sessions` - Create a new reading session
- `GET /sessions/{id}` - Get a specific reading session
- `PUT /sessions/{id}` - Update a reading session
- `DELETE /sessions/{id}` - Delete a reading session

## License

MIT
