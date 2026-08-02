"""
backend/logging_config.py
Configures structured, rotating file logging and console logging.
Writes to logs/app.log and stdout.
"""
from __future__ import annotations

import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logging() -> logging.Logger:
    """Sets up a rotating file handler and a stream handler for logging."""
    # Find root project path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, "app.log")

    logger = logging.getLogger("ai_resume")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers being added if setup is run multiple times
    if not logger.handlers:
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 1. Rotating File Handler (max 5MB, keeps last 3 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 2. Console (Stdout) Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# Expose a global logger
logger = setup_logging()
