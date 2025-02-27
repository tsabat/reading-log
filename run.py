import os
import sys

import uvicorn

from app.db.init_db import init_db


def main():
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    # Initialize the database
    print("Initializing database...")
    if not init_db():
        print("Failed to initialize database. Exiting.")
        sys.exit(1)

    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8888))

    # Run the application
    print(f"Starting FastAPI application on port {port}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    main()
