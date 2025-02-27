# Reading Tracker App

A simple web application to track your reading sessions, built with SvelteKit and FastAPI.

## Features

- Track reading sessions with date and duration
- View all your reading sessions
- Edit or delete existing sessions
- See statistics about your total reading time

## Tech Stack

### Frontend
- SvelteKit
- TypeScript
- Vite

### Backend
- FastAPI
- SQLObject (ORM)
- Uvicorn (ASGI server)

## Getting Started

### Prerequisites

- Node.js (v16+)
- npm or yarn
- Python 3.8+
- Poetry (Python package manager)

### Running the Backend

1. Navigate to the project root directory
2. Install dependencies:
   ```
   poetry install
   ```
3. Run the FastAPI server:
   ```
   python play/run.py
   ```
   The API will be available at http://localhost:8888

### Running the Frontend

1. Navigate to the frontend directory:
   ```
   cd play/frontend
   ```
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm run dev
   ```
   The frontend will be available at http://localhost:5173

## API Endpoints

- `GET /sessions` - Get all reading sessions
- `POST /sessions` - Create a new reading session
- `GET /sessions/{id}` - Get a specific reading session
- `PUT /sessions/{id}` - Update a reading session
- `DELETE /sessions/{id}` - Delete a reading session

## License

MIT
