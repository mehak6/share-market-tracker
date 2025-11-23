"""
Centralized Configuration Constants
All application-wide constants in one place for easy maintenance
"""
from typing import Final

# API Configuration
API_RATE_LIMIT_SECONDS: Final[float] = 0.1  # 100ms between API calls
API_RETRY_ATTEMPTS: Final[int] = 3
API_TIMEOUT_SECONDS: Final[int] = 10
API_BATCH_THRESHOLD: Final[int] = 5  # Use batch fetch if more than 5 symbols

# Tax Configuration (FY 2024-25 India)
STCG_RATE: Final[float] = 0.156  # 15.6% (15% + surcharge/cess)
LTCG_RATE: Final[float] = 0.104  # 10.4% (10% + surcharge/cess)
LTCG_EXEMPTION_AMOUNT: Final[float] = 100000  # ₹1 lakh
LTCG_HOLDING_PERIOD_DAYS: Final[int] = 365  # 1 year
STCG_HOLDING_PERIOD_DAYS: Final[int] = 0  # Less than 1 year

# Tax Types
TAX_TYPE_STCG: Final[str] = 'STCG'
TAX_TYPE_LTCG: Final[str] = 'LTCG'

# Transaction Types
TRANSACTION_TYPE_DEPOSIT: Final[str] = 'deposit'
TRANSACTION_TYPE_WITHDRAWAL: Final[str] = 'withdrawal'

# Dividend Types
DIVIDEND_TYPE_REGULAR: Final[str] = 'regular'
DIVIDEND_TYPE_SPECIAL: Final[str] = 'special'
DIVIDEND_TYPE_BONUS: Final[str] = 'bonus'

# Corporate Action Types
ADJUSTMENT_TYPE_SPLIT: Final[str] = 'split'
ADJUSTMENT_TYPE_BONUS: Final[str] = 'bonus'
ADJUSTMENT_TYPE_RIGHTS: Final[str] = 'rights'

# UI Configuration
DEFAULT_WINDOW_WIDTH: Final[int] = 1200
DEFAULT_WINDOW_HEIGHT: Final[int] = 800
MIN_WINDOW_WIDTH: Final[int] = 800
MIN_WINDOW_HEIGHT: Final[int] = 600

# Database Configuration
DB_CONNECTION_TIMEOUT: Final[int] = 30
DB_ENABLE_WAL_MODE: Final[bool] = True
DB_ENABLE_FOREIGN_KEYS: Final[bool] = True
PRICE_CACHE_STALE_MINUTES: Final[int] = 15

# Validation Constraints
MIN_QUANTITY: Final[float] = 0.0001  # Support fractional shares
MIN_PRICE: Final[float] = 0.01  # Minimum ₹0.01
MAX_QUANTITY: Final[float] = 1000000000  # 1 billion shares max
MAX_PRICE: Final[float] = 10000000  # ₹1 crore max per share

# Date Format
DATE_FORMAT: Final[str] = "%Y-%m-%d"
DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

# Expense Categories
EXPENSE_CATEGORIES: Final[list] = [
    'Electricity',
    'Rent',
    'Food',
    'Transportation',
    'Healthcare',
    'Entertainment',
    'Education',
    'Shopping',
    'Other'
]

# Logging Configuration
LOG_FORMAT: Final[str] = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT: Final[str] = '%Y-%m-%d %H:%M:%S'
LOG_FILE: Final[str] = 'sharetracker.log'
LOG_MAX_BYTES: Final[int] = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT: Final[int] = 5

# Performance Settings
REFRESH_DELAY_MS: Final[int] = 100  # Delay between price updates in milliseconds
THREAD_POOL_SIZE: Final[int] = 5  # Number of worker threads for background tasks

# Price Alert Settings
DEFAULT_STOP_LOSS_PERCENT: Final[float] = 5.0  # Default 5% stop-loss
DEFAULT_PROFIT_TARGET_PERCENT: Final[float] = 10.0  # Default 10% profit target
MIN_ALERT_VALUE: Final[float] = 0.01  # Minimum alert target value
MAX_ALERT_VALUE: Final[float] = 10000000  # Maximum alert target (₹1 crore)
MAX_ALERT_PERCENTAGE: Final[float] = 100.0  # Maximum percentage for alerts
