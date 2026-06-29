"""
Centralized logging configuration for the entire system
"""

import logging
import logging.handlers
from config.config import settings
from pathlib import Path

# Create logs directory if not exists
Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)

def setup_logger(name: str) -> logging.Logger:
    """
    Setup logger with both file and console handlers

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # ============ FILE HANDLER ============
    file_handler = logging.handlers.RotatingFileHandler(
        filename=settings.log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, settings.log_level))
    file_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # ============ CONSOLE HANDLER ============
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level))
    console_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger
