import os

from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

# Get database URL from environment variable or use SQLite as default
DATABASE_URL = os.getenv("DATABASE_URL")

# Determine which database to use based on DATABASE_URL
if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    # Use PostgreSQL in production
    engine = create_engine(DATABASE_URL, echo=False)
else:
    # Use SQLite for local development
    SQLITE_DATABASE_URL = "sqlite:///./reading_app.db"
    engine = create_engine(
        SQLITE_DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
    )


def create_db_and_tables() -> None:
    """Create database tables if they don't exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get a database session."""
    with Session(engine) as session:
        yield session
