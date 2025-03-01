import os

from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)

# Get database URL from environment variable or use SQLite as default
DATABASE_URL = os.getenv("DATABASE_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Determine which database to use based on DATABASE_URL
if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    # Use PostgreSQL in production
    logger.info("Using PostgreSQL database")
    # Railway provides DATABASE_URL in the format: postgresql://postgres:password@containers-us-west-1.railway.app:5432/railway
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
else:
    # Use SQLite for local development
    logger.info("Using SQLite database for local development")
    SQLITE_DATABASE_URL = "sqlite:///./reading_app.db"
    engine = create_engine(
        SQLITE_DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
    )


def create_db_and_tables() -> None:
    """Create database tables if they don't exist."""
    logger.info("Creating database tables if they don't exist")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def get_session() -> Generator[Session, None, None]:
    """Get a database session."""
    with Session(engine) as session:
        yield session
