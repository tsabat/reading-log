from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.reading_logs import router as reading_logs_router
from app.api.sessions import router as sessions_router
from app.db.database import create_db_and_tables

# Load environment variables from .env file
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI application.
    Creates database tables on startup.
    """
    # Create database tables on startup
    create_db_and_tables()
    yield


# Create FastAPI application
app = FastAPI(
    title="Reading App API",
    description="API for tracking reading sessions and logs",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions_router)
app.include_router(reading_logs_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Reading App API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
