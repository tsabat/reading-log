import os
import sys

from pathlib import Path

import uvicorn

from app.db.init_db import init_db
from app.logger import get_logger

logger = get_logger(__name__)


def main():
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Initialize the database
    logger.info("Initializing database...")
    if not init_db():
        logger.error("Failed to initialize database. Exiting.")
        sys.exit(1)

    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8888))

    # Run the application
    logger.info("Starting FastAPI application on port %s...", port)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)  # noqa: S104


if __name__ == "__main__":
    main()
