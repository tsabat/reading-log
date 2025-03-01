import os
import traceback

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    try:
        # Log startup information
        logger.info("Application starting up...")
        logger.info("Environment: %s", os.getenv("ENVIRONMENT", "development"))

        # Create database tables on startup
        create_db_and_tables()
        logger.info("Application startup complete")
        yield
        logger.info("Application shutting down...")
    except Exception as e:
        logger.exception("Error during application lifecycle: %s", str(e))
        raise


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


# Add exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to log all unhandled exceptions."""
    error_id = os.urandom(8).hex()
    logger.error(
        "Unhandled exception: %s (Error ID: %s)\n%s",
        str(exc),
        error_id,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "error_id": error_id,
        },
    )


# Include routers
app.include_router(reading_logs_router)


@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
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
        logger.info("Health check passed")
    except Exception as e:
        logger.exception("Database health check failed: %s", str(e))
        db_status = "unhealthy"
        raise HTTPException(status_code=500, detail="Database connection failed")

    return {
        "status": "healthy",
        "database": db_status,
        "version": app.version,
    }
