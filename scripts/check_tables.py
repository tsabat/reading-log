#!/usr/bin/env python
"""
Script to check if tables exist in the database and create them if they don't.
This script is intended to be run after the application has started to verify tables.
"""

import os
import sys
import traceback

from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

import psycopg2

from dotenv import load_dotenv
from sqlalchemy import inspect
from sqlmodel import Session, SQLModel, create_engine

from app.support.logging_support import get_logger

# Set up logger
logger = get_logger(__name__)


def main():
    """Check if tables exist in the database and create them if they don't."""
    # Load environment variables
    load_dotenv()

    logger.info("Checking if tables exist in the database...")

    # Get database URL from environment variable
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)

    # Log the database URL (masking password)
    if ":" in database_url and "@" in database_url:
        masked_url = (
            database_url.split("@")[0].split(":")[0]
            + ":***@"
            + database_url.split("@")[1]
        )
        logger.info("DATABASE_URL: %s", masked_url)

    # Import all models to ensure they're registered with SQLModel
    try:
        logger.info("Importing models...")
        from app.models.reading_log import ReadingLog

        # Log the imported models
        models = [ReadingLog]
        model_names = [model.__name__ for model in models]
        logger.info("Imported models: %s", ", ".join(model_names))

        # Get expected table names
        expected_tables = [
            getattr(model, "__tablename__", model.__name__.lower()) for model in models
        ]
        logger.info("Expected tables: %s", expected_tables)
    except Exception as e:
        logger.exception(
            "Error importing models: %s\n%s", str(e), traceback.format_exc()
        )
        sys.exit(1)

    try:
        # Create SQLAlchemy engine
        if database_url.startswith("postgresql"):
            # Fix for Railway's PostgreSQL URL format
            if not database_url.startswith("postgresql+psycopg2://"):
                database_url = database_url.replace(
                    "postgresql://", "postgresql+psycopg2://"
                )
                logger.info("Modified DATABASE_URL to use psycopg2 driver")

            engine = create_engine(
                database_url,
                echo=True,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 10},
            )
        else:
            engine = create_engine(
                database_url, echo=True, connect_args={"check_same_thread": False}
            )

        logger.info("Engine created successfully")

        # Check if tables exist using SQLAlchemy inspector
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.info("Existing tables in database: %s", existing_tables)

        # Check if expected tables exist
        missing_tables = [
            table
            for table in expected_tables
            if table.lower() not in [t.lower() for t in existing_tables]
        ]

        if missing_tables:
            logger.warning("Missing tables: %s", missing_tables)

            # Try to create missing tables
            logger.info("Attempting to create missing tables...")

            # Ensure metadata is up-to-date
            metadata_tables = list(SQLModel.metadata.tables.keys())
            logger.info("Tables in SQLModel metadata: %s", metadata_tables)

            # Create all tables
            SQLModel.metadata.create_all(engine)
            logger.info("Created all tables from metadata")

            # Check again if tables exist
            inspector = inspect(engine)
            existing_tables_after = inspector.get_table_names()
            logger.info("Tables after creation: %s", existing_tables_after)

            # Check if tables were created
            still_missing = [
                table
                for table in expected_tables
                if table.lower() not in [t.lower() for t in existing_tables_after]
            ]

            if still_missing:
                logger.error("Failed to create tables: %s", still_missing)

                # Try direct SQL approach
                logger.info("Attempting to create tables with direct SQL...")

                # Connect to PostgreSQL directly
                if database_url.startswith("postgresql"):
                    try:
                        # Parse the database URL
                        url_parts = database_url.replace(
                            "postgresql+psycopg2://", ""
                        ).split("@")
                        credentials = url_parts[0].split(":")
                        username = credentials[0]
                        password = credentials[1]

                        host_parts = url_parts[1].split("/")
                        host_port = host_parts[0].split(":")
                        hostname = host_port[0]
                        port = int(host_port[1]) if len(host_port) > 1 else 5432
                        database = host_parts[1]

                        # Connect to PostgreSQL
                        conn = psycopg2.connect(
                            host=hostname,
                            port=port,
                            user=username,
                            password=password,
                            dbname=database,
                            connect_timeout=10,
                        )
                        conn.autocommit = True
                        cur = conn.cursor()

                        # Create reading_log table directly
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS reading_log (
                                id SERIAL PRIMARY KEY,
                                duration INTEGER NOT NULL,
                                description TEXT,
                                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP
                            );
                        """)
                        logger.info("Created reading_log table with direct SQL")

                        # Check if table was created
                        cur.execute(
                            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'reading_log');"
                        )
                        table_exists = cur.fetchone()[0]
                        logger.info("reading_log table exists: %s", table_exists)

                        # Close cursor and connection
                        cur.close()
                        conn.close()
                    except Exception as e:
                        logger.exception(
                            "Error creating tables with direct SQL: %s\n%s",
                            str(e),
                            traceback.format_exc(),
                        )
            else:
                logger.info("All tables created successfully!")
        else:
            logger.info("All expected tables exist in the database!")

            # Check table structure
            with Session(engine) as session:
                try:
                    # Try a simple query to verify table structure
                    from sqlalchemy import text

                    result = session.execute(text("SELECT * FROM reading_log LIMIT 1"))
                    columns = result.keys()
                    logger.info("reading_log table columns: %s", columns)
                except Exception as e:
                    logger.exception(
                        "Error querying table: %s\n%s", str(e), traceback.format_exc()
                    )

        return True
    except Exception as e:
        logger.exception(
            "Error checking tables: %s\n%s", str(e), traceback.format_exc()
        )
        return False


if __name__ == "__main__":
    success = main()
    if success:
        logger.info("Table check completed successfully!")
        sys.exit(0)
    else:
        logger.error("Table check failed!")
        sys.exit(1)
