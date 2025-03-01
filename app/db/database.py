import os
import time

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
    # Railway provides DATABASE_URL in the format: postgresql://postgres:password@containers-us-west-1.railway.app:5432/railway
    try:
        engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,  # Recycle connections after 5 minutes
            connect_args={"connect_timeout": 10},  # 10 seconds connection timeout
        )
        logger.info("PostgreSQL engine created successfully")
    except Exception as e:
        logger.exception("Failed to create PostgreSQL engine: %s", str(e))
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
        logger.exception("Failed to create SQLite engine: %s", str(e))
        raise


def create_db_and_tables() -> None:
    """Create database tables if they don't exist."""
    logger.info("Creating database tables if they don't exist")

    for attempt in range(MAX_RETRIES):
        try:
            SQLModel.metadata.create_all(engine)
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
                    "Failed to create database tables after %s attempts: %s",
                    MAX_RETRIES,
                    str(e),
                )
                raise
        except Exception as e:
            logger.exception("Error creating database tables: %s", str(e))
            raise


def get_session() -> Generator[Session, None, None]:
    """Get a database session."""
    session = None
    try:
        session = Session(engine)
        yield session
    except SQLAlchemyError as e:
        logger.exception("Database session error: %s", str(e))
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()
