from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.api.reading_logs import router as reading_logs_router
from app.db.database import create_db_and_tables, get_session
from app.models import ReadingLog
from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)

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
    description="API for tracking reading logs",
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
app.include_router(reading_logs_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Reading App API"}


@app.get("/health")
async def health(db: Session = Depends(get_session)):
    """
    Health check endpoint.
    Checks if the application is running and if the database is accessible.
    """
    try:
        # Try to execute a simple query to check database connectivity
        db.exec(select(ReadingLog).limit(1))
        db_status = "healthy"
    except Exception as e:
        logger.error("Database health check failed: %s", str(e))
        db_status = "unhealthy"
        raise HTTPException(status_code=500, detail="Database connection failed")

    return {
        "status": "healthy",
        "database": db_status,
        "version": app.version,
    }
