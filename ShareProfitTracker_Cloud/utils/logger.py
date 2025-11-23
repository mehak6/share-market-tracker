"""
Centralized Logging Configuration
Provides consistent logging across the application
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

# Import constants
try:
    from config.constants import LOG_FORMAT, LOG_DATE_FORMAT, LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT
except ImportError:
    # Fallback defaults
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    LOG_FILE = 'sharetracker.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024
    LOG_BACKUP_COUNT = 5


class LoggerSetup:
    """Centralized logger configuration"""

    _initialized = False
    _log_file_path: Optional[Path] = None

    @classmethod
    def setup_logger(cls, name: str = 'ShareTracker', level: int = logging.INFO) -> logging.Logger:
        """
        Set up and return a configured logger

        Args:
            name: Logger name (typically module name)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)

        # Only configure root logger once
        if not cls._initialized and name == 'ShareTracker':
            cls._configure_root_logger(logger, level)
            cls._initialized = True

        return logger

    @classmethod
    def _configure_root_logger(cls, logger: logging.Logger, level: int):
        """Configure the root logger with handlers"""
        logger.setLevel(level)

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)

        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler with rotation
        try:
            log_dir = Path.cwd() / 'logs'
            log_dir.mkdir(exist_ok=True)
            cls._log_file_path = log_dir / LOG_FILE

            file_handler = RotatingFileHandler(
                cls._log_file_path,
                maxBytes=LOG_MAX_BYTES,
                backupCount=LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            logger.info(f"Logging initialized. Log file: {cls._log_file_path}")
        except Exception as e:
            # If file logging fails, continue with console only
            logger.warning(f"Could not set up file logging: {e}")

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module

        Args:
            name: Module name (use __name__)

        Returns:
            Logger instance
        """
        return logging.getLogger(f'ShareTracker.{name}')


# Convenience function
def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get a logger for the calling module

    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Application started")

    Args:
        name: Module name (pass __name__)

    Returns:
        Configured logger instance
    """
    return LoggerSetup.get_logger(name)


# Initialize root logger on import
LoggerSetup.setup_logger('ShareTracker', logging.INFO)
