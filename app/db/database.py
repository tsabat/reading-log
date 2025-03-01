import os
import socket
import time
import traceback

from typing import Generator

from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine

from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)

# Get database URL from environment variable or use SQLite as default
DATABASE_URL = os.getenv("DATABASE_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Maximum number of connection retries
MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds

# Determine which database to use based on DATABASE_URL
if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    # Use PostgreSQL in production
    logger.info("Using PostgreSQL database")

    # Log the database URL (masking password)
    masked_url = (
        DATABASE_URL.split("@")[0].split(":")[0] + ":***@" + DATABASE_URL.split("@")[1]
    )
    logger.info("Original DATABASE_URL: %s", masked_url)

    # Fix for Railway's PostgreSQL URL format
    # Railway provides DATABASE_URL in the format: postgresql://postgres:password@postgres.railway.internal:5432/railway
    # But SQLAlchemy expects: postgresql+psycopg2://postgres:password@postgres.railway.internal:5432/railway
    if not DATABASE_URL.startswith("postgresql+psycopg2://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
        logger.info("Modified DATABASE_URL to use psycopg2 driver")

    # Check if we're using Railway's internal PostgreSQL
    if "railway.internal" in DATABASE_URL:
        logger.info("Using Railway's internal PostgreSQL")

        # Try to resolve the hostname
        try:
            hostname = DATABASE_URL.split("@")[1].split("/")[0].split(":")[0]
            logger.info("Attempting to resolve hostname: %s", hostname)
            ip_address = socket.gethostbyname(hostname)
            logger.info("Hostname resolved to IP: %s", ip_address)
        except Exception as e:
            logger.warning("Failed to resolve hostname: %s", str(e))

            # If hostname is postgres.railway.internal, try to use the PGHOST environment variable
            if hostname == "postgres.railway.internal":
                pghost = os.getenv("PGHOST")
                if pghost:
                    logger.info("Using PGHOST environment variable: %s", pghost)
                    # Update the DATABASE_URL with the PGHOST value
                    DATABASE_URL = DATABASE_URL.replace(
                        "postgres.railway.internal", pghost
                    )
                    logger.info("Updated DATABASE_URL with PGHOST")

    try:
        logger.info("Connecting to PostgreSQL database...")
        engine = create_engine(
            DATABASE_URL,
            echo=True,  # Set to True to see all SQL queries for debugging
            pool_pre_ping=True,
            pool_recycle=300,  # Recycle connections after 5 minutes
            connect_args={"connect_timeout": 10},  # 10 seconds connection timeout
        )
        logger.info("PostgreSQL engine created successfully")
    except Exception as e:
        logger.exception(
            "Failed to create PostgreSQL engine: %s\n%s", str(e), traceback.format_exc()
        )
        raise
else:
    # Use SQLite for local development
    logger.info("Using SQLite database for local development")
    SQLITE_DATABASE_URL = "sqlite:///./reading_app.db"
    try:
        engine = create_engine(
            SQLITE_DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
        )
        logger.info("SQLite engine created successfully")
    except Exception as e:
        logger.exception(
            "Failed to create SQLite engine: %s\n%s", str(e), traceback.format_exc()
        )
        raise


def create_db_and_tables() -> None:
    """Create database tables if they don't exist."""
    logger.info("Creating database tables if they don't exist")

    # Import all models to ensure they're registered with SQLModel
    # This is important to make sure all tables are created
    logger.info("Imported models: ReadingLog")

    for attempt in range(MAX_RETRIES):
        try:
            # Create all tables defined in SQLModel metadata
            SQLModel.metadata.create_all(engine)

            # Verify tables were created by listing them
            from sqlalchemy import inspect

            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info("Tables in database: %s", tables)

            logger.info("Database tables created successfully")
            return
        except OperationalError as e:
            if attempt < MAX_RETRIES - 1:
                logger.warning(
                    "Database connection failed (attempt %s/%s): %s. Retrying in %s seconds...",
                    attempt + 1,
                    MAX_RETRIES,
                    str(e),
                    RETRY_DELAY,
                )
                time.sleep(RETRY_DELAY)
            else:
                logger.exception(
                    "Failed to create database tables after %s attempts: %s\n%s",
                    MAX_RETRIES,
                    str(e),
                    traceback.format_exc(),
                )
                raise
        except Exception as e:
            logger.exception(
                "Error creating database tables: %s\n%s", str(e), traceback.format_exc()
            )
            raise


def get_session() -> Generator[Session, None, None]:
    """Get a database session."""
    session = None
    try:
        session = Session(engine)
        yield session
    except SQLAlchemyError as e:
        logger.exception(
            "Database session error: %s\n%s", str(e), traceback.format_exc()
        )
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()
