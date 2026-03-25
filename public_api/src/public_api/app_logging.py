"""
Logging configuration for the application.
"""

import logging

from public_api.config import settings


def setup_logging():
    """Configure the application's logging."""
    logging.basicConfig(
        filename=settings.log_file,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
