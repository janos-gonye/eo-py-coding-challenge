"""
Logging configuration for the application.
"""

import logging
from pathlib import Path

from public_api.config import settings


def setup_logging():
    """Configure the application's logging."""
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=str(log_file),
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
