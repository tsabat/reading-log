FROM python:3.12-slim

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not use a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x scripts/*.py

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8888
ENV HOST=0.0.0.0

# Expose the port
EXPOSE 8888

# Run the application using the Railway start script
CMD ["sh", "-c", "python scripts/postgres_diagnostic.py && python scripts/railway_migrate.py && python scripts/railway_start.py"]
