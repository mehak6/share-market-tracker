#!/usr/bin/env python3
"""
Share Profit Tracker - Improved Version
Entry point with enhanced logging, error handling, and validation
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Initialize logging first
try:
    from utils.logger import get_logger, LoggerSetup
    import logging

    # Set up root logger
    LoggerSetup.setup_logger('ShareTracker', logging.INFO)
    logger = get_logger(__name__)
    logger.info("="*60)
    logger.info("Share Profit Tracker - Improved Version Starting")
    logger.info("="*60)

except Exception as e:
    print(f"Warning: Could not initialize logging: {e}")
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Import configuration
try:
    from config.constants import (
        DEFAULT_WINDOW_WIDTH,
        DEFAULT_WINDOW_HEIGHT,
        MIN_WINDOW_WIDTH,
        MIN_WINDOW_HEIGHT
    )
    logger.info("Configuration loaded successfully")
except ImportError as e:
    logger.warning(f"Could not load configuration: {e}")
    # Fallback values
    DEFAULT_WINDOW_WIDTH = 1200
    DEFAULT_WINDOW_HEIGHT = 800
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 600

# Import improved modules with fallback to original
try:
    from data.database_improved import DatabaseManager, ValidationError
    logger.info("Using improved DatabaseManager")
except ImportError:
    logger.warning("Falling back to original DatabaseManager")
    from data.database import DatabaseManager
    ValidationError = ValueError

try:
    from data.models_improved import Stock, PortfolioSummary
    logger.info("Using improved data models")
except ImportError:
    logger.warning("Falling back to original data models")
    from data.models import Stock, PortfolioSummary

# Import GUI (uses original but with improved backend)
try:
    from gui.main_window import MainWindow
    logger.info("GUI module loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import GUI: {e}")
    print(f"Error: Could not load GUI module: {e}")
    sys.exit(1)

# Import utilities
try:
    from utils.config import AppConfig
    logger.info("AppConfig loaded")
except ImportError as e:
    logger.warning(f"Could not load AppConfig: {e}")
    AppConfig = None


def ensure_directories():
    """Ensure required directories exist"""
    try:
        directories = [
            'logs',
            'backups',
            'exports',
            'data'
        ]

        for dir_name in directories:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {dir_name}")

    except Exception as e:
        logger.error(f"Error creating directories: {e}")


def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []

    # Check for yfinance
    try:
        import yfinance
        logger.info("yfinance available")
    except ImportError:
        missing_deps.append("yfinance")
        logger.warning("yfinance not available - will use mock data")

    # Check for pandas
    try:
        import pandas
        logger.info("pandas available")
    except ImportError:
        missing_deps.append("pandas")
        logger.warning("pandas not available")

    # Check for openpyxl
    try:
        import openpyxl
        logger.info("openpyxl available")
    except ImportError:
        missing_deps.append("openpyxl")
        logger.warning("openpyxl not available - Excel export may not work")

    if missing_deps:
        logger.warning(f"Missing dependencies: {', '.join(missing_deps)}")
        logger.info("Application will continue with limited functionality")

    return missing_deps


def initialize_database():
    """Initialize database with error handling"""
    try:
        db_path = "portfolio.db"
        if AppConfig:
            db_path = AppConfig.get_database_path()

        logger.info(f"Initializing database: {db_path}")
        db_manager = DatabaseManager(db_path)
        logger.info("Database initialized successfully")
        return db_manager

    except Exception as e:
        logger.exception(f"Failed to initialize database: {e}")
        raise


def main():
    """Main application entry point with comprehensive error handling"""

    try:
        # Log application start
        logger.info("Application starting...")

        # Ensure directories exist
        logger.info("Creating required directories...")
        ensure_directories()

        # Check dependencies
        logger.info("Checking dependencies...")
        missing_deps = check_dependencies()

        # Ensure AppConfig directories if available
        if AppConfig:
            try:
                AppConfig.ensure_directories()
                logger.info("AppConfig directories ensured")
            except Exception as e:
                logger.error(f"Error with AppConfig: {e}")

        # Initialize database
        logger.info("Initializing database...")
        db_manager = initialize_database()

        # Create and run the application
        logger.info("Creating main window...")
        app = MainWindow()

        logger.info("="*60)
        logger.info("Application ready! Starting event loop...")
        logger.info("="*60)

        # Run the application
        app.run()

        logger.info("Application closed normally")

    except KeyboardInterrupt:
        logger.info("Application interrupted by user (Ctrl+C)")
        sys.exit(0)

    except ImportError as e:
        logger.exception(f"Import error: {e}")
        print("\n" + "="*60)
        print("ERROR: Missing Required Module")
        print("="*60)
        print(f"\nError: {e}")
        print("\nPlease ensure all required packages are installed:")
        print("  pip install -r requirements.txt")
        print("\nRequired packages:")
        print("  - yfinance>=0.2.18")
        print("  - pandas>=2.0.0")
        print("  - openpyxl>=3.1.0")
        print("="*60)
        input("\nPress Enter to exit...")
        sys.exit(1)

    except ValidationError as e:
        logger.exception(f"Validation error during startup: {e}")
        print("\n" + "="*60)
        print("ERROR: Data Validation Failed")
        print("="*60)
        print(f"\nError: {e}")
        print("\nThe application encountered invalid data during startup.")
        print("Please check your database or configuration.")
        print("="*60)
        input("\nPress Enter to exit...")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Unexpected error during startup: {e}")
        print("\n" + "="*60)
        print("ERROR: Application Failed to Start")
        print("="*60)
        print(f"\nError: {e}")
        print(f"\nError Type: {type(e).__name__}")
        print("\nPlease check the log file for details:")
        print("  logs/sharetracker.log")
        print("\nIf the problem persists, please report this error.")
        print("="*60)
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
