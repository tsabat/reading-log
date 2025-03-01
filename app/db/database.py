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

    # Explicitly import all models to ensure they're registered with SQLModel
    # This is important to make sure all tables are created
    try:
        # Import all models here to ensure they're registered
        from app.models.reading_log import ReadingLog

        # Log the imported models and their __tablename__ attributes
        models = [ReadingLog]
        model_names = [model.__name__ for model in models]
        logger.info("Imported models: %s", ", ".join(model_names))

        # Log the table names that will be created
        table_names = [
            getattr(model, "__tablename__", model.__name__.lower()) for model in models
        ]
        logger.info("Tables to be created: %s", table_names)

        # Log the tables in the metadata
        metadata_tables = list(SQLModel.metadata.tables.keys())
        logger.info("Tables in SQLModel metadata: %s", metadata_tables)
    except Exception as e:
        logger.exception(
            "Error importing models: %s\n%s", str(e), traceback.format_exc()
        )
        raise

    for attempt in range(MAX_RETRIES):
        try:
            # Create all tables defined in SQLModel metadata
            SQLModel.metadata.create_all(engine)

            # Verify tables were created by listing them
            from sqlalchemy import inspect

            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info("Tables in database: %s", tables)

            # Check if our expected tables are in the database
            missing_tables = [
                table
                for table in table_names
                if table.lower() not in [t.lower() for t in tables]
            ]
            if missing_tables:
                logger.warning("Some expected tables are missing: %s", missing_tables)

                # Try to create the missing tables directly with SQL
                with Session(engine) as _session:
                    for model_class in models:
                        table_name = getattr(
                            model_class, "__tablename__", model_class.__name__.lower()
                        )
                        if table_name.lower() in [t.lower() for t in missing_tables]:
                            logger.info(
                                "Attempting to create missing table %s directly with SQL",
                                table_name,
                            )
                            try:
                                # Create the table directly using SQLModel's create_all with a subset of tables
                                # This avoids the need to access __table__ directly
                                model_metadata = SQLModel.metadata
                                tables_to_create = [
                                    table
                                    for name, table in model_metadata.tables.items()
                                    if name.lower() == table_name.lower()
                                ]
                                if tables_to_create:
                                    model_metadata.create_all(
                                        engine, tables=tables_to_create
                                    )
                                    logger.info("Created table %s directly", table_name)
                                else:
                                    logger.warning(
                                        "Could not find table %s in metadata",
                                        table_name,
                                    )
                            except Exception as e:
                                logger.exception(
                                    "Failed to create table %s directly: %s\n%s",
                                    table_name,
                                    str(e),
                                    traceback.format_exc(),
                                )

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
