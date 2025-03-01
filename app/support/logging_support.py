import logging

from rich.logging import RichHandler

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

# Create a function to get loggers


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
