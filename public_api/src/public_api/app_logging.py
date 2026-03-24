"""
Logging configuration for the application.
"""

import logging


def setup_logging():
    """Configure the application's logging."""
    logging.basicConfig(
        filename="public_api.log",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
