"""
Improved Database Manager with proper logging, validation, and error handling
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

# Import logging and constants
try:
    from utils.logger import get_logger
    from config.constants import (
        DB_ENABLE_WAL_MODE, DB_ENABLE_FOREIGN_KEYS,
        TRANSACTION_TYPE_DEPOSIT, TRANSACTION_TYPE_WITHDRAWAL,
        MIN_QUANTITY, MIN_PRICE, MAX_QUANTITY, MAX_PRICE,
        DATE_FORMAT
    )
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

    # Fallback constants
    DB_ENABLE_WAL_MODE = True
    DB_ENABLE_FOREIGN_KEYS = True
    TRANSACTION_TYPE_DEPOSIT = 'deposit'
    TRANSACTION_TYPE_WITHDRAWAL = 'withdrawal'
    MIN_QUANTITY = 0.0001
    MIN_PRICE = 0.01
    MAX_QUANTITY = 1000000000
    MAX_PRICE = 10000000
    DATE_FORMAT = "%Y-%m-%d"

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class DatabaseManager:
    """
    Improved Database Manager with:
    - Proper logging
    - Input validation
    - Specific exception handling
    - PRAGMA settings for safety
    - Better error messages
    """

    def __init__(self, db_path: str = "portfolio.db"):
        self.db_path = db_path
        logger.info(f"Initializing DatabaseManager with path: {db_path}")
        try:
            self.init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.exception(f"Failed to initialize database: {e}")
            raise

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection with proper configuration

        Returns:
            Configured SQLite connection

        Raises:
            sqlite3.Error: If connection fails
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            # Enable foreign key constraints
            if DB_ENABLE_FOREIGN_KEYS:
                conn.execute('PRAGMA foreign_keys = ON')

            # Enable WAL mode for better concurrency
            if DB_ENABLE_WAL_MODE:
                conn.execute('PRAGMA journal_mode = WAL')

            return conn

        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def init_database(self):
        """Initialize database schema with all tables and indexes"""
        try:
            with self.get_connection() as conn:
                logger.debug("Creating database schema")
                conn.executescript('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        display_name TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS stocks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        symbol TEXT NOT NULL,
                        company_name TEXT,
                        quantity REAL NOT NULL,
                        purchase_price REAL NOT NULL,
                        purchase_date TEXT NOT NULL,
                        broker TEXT,
                        cash_invested REAL DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    );

                    CREATE TABLE IF NOT EXISTS price_cache (
                        symbol TEXT PRIMARY KEY,
                        current_price REAL,
                        last_updated TEXT
                    );

                    CREATE TABLE IF NOT EXISTS cash_transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        transaction_type TEXT NOT NULL,
                        amount REAL NOT NULL,
                        description TEXT,
                        transaction_date TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    );

                    CREATE TABLE IF NOT EXISTS other_expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        description TEXT NOT NULL,
                        amount REAL NOT NULL,
                        expense_date TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    );

                    CREATE TABLE IF NOT EXISTS dividends (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        symbol TEXT NOT NULL,
                        company_name TEXT,
                        dividend_per_share REAL NOT NULL,
                        total_dividend REAL NOT NULL,
                        shares_held REAL NOT NULL,
                        ex_dividend_date TEXT NOT NULL,
                        payment_date TEXT,
                        record_date TEXT,
                        dividend_type TEXT DEFAULT 'regular',
                        tax_deducted REAL DEFAULT 0,
                        net_dividend REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    );

                    CREATE TABLE IF NOT EXISTS stock_adjustments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        adjustment_type TEXT NOT NULL,
                        adjustment_date TEXT NOT NULL,
                        ratio_from INTEGER NOT NULL,
                        ratio_to INTEGER NOT NULL,
                        description TEXT,
                        shares_before REAL,
                        shares_after REAL,
                        price_before REAL,
                        price_after REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    );
                ''')

                # Create indexes for performance
                self._create_indexes(conn)

                # Migrate existing schema (add columns if missing)
                self._migrate_schema(conn)

                conn.commit()
                logger.debug("Database schema created successfully")

        except sqlite3.Error as e:
            logger.exception(f"Database initialization failed: {e}")
            raise

        # Initialize default users
        self.init_default_users()

    def _create_indexes(self, conn: sqlite3.Connection):
        """Create database indexes for performance"""
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_stocks_user_symbol ON stocks(user_id, symbol)',
            'CREATE INDEX IF NOT EXISTS idx_stocks_user_id ON stocks(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_price_cache_symbol ON price_cache(symbol)',
            'CREATE INDEX IF NOT EXISTS idx_price_cache_updated ON price_cache(last_updated)',
            'CREATE INDEX IF NOT EXISTS idx_cash_transactions_user ON cash_transactions(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_cash_transactions_date ON cash_transactions(transaction_date)',
            'CREATE INDEX IF NOT EXISTS idx_other_expenses_user ON other_expenses(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_other_expenses_date ON other_expenses(expense_date)',
            'CREATE INDEX IF NOT EXISTS idx_dividends_user ON dividends(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_dividends_symbol ON dividends(symbol)',
        ]

        for index_sql in indexes:
            try:
                conn.execute(index_sql)
                logger.debug(f"Index created: {index_sql.split('idx_')[1].split(' ON')[0]}")
            except sqlite3.OperationalError as e:
                logger.debug(f"Index already exists or creation failed: {e}")

    def _migrate_schema(self, conn: sqlite3.Connection):
        """Add missing columns to existing tables"""
        migrations = [
            ('stocks', 'cash_invested', 'ALTER TABLE stocks ADD COLUMN cash_invested REAL DEFAULT 0'),
            ('stocks', 'user_id', 'ALTER TABLE stocks ADD COLUMN user_id INTEGER DEFAULT 1'),
            ('cash_transactions', 'user_id', 'ALTER TABLE cash_transactions ADD COLUMN user_id INTEGER DEFAULT 1'),
            ('other_expenses', 'user_id', 'ALTER TABLE other_expenses ADD COLUMN user_id INTEGER DEFAULT 1'),
            ('dividends', 'user_id', 'ALTER TABLE dividends ADD COLUMN user_id INTEGER DEFAULT 1'),
        ]

        for table, column, sql in migrations:
            try:
                conn.execute(sql)
                logger.debug(f"Added column {column} to {table}")
            except sqlite3.OperationalError:
                logger.debug(f"Column {column} already exists in {table}")

    def _validate_stock_data(self, quantity: float, purchase_price: float, purchase_date: str):
        """
        Validate stock input data

        Args:
            quantity: Number of shares
            purchase_price: Price per share
            purchase_date: Purchase date in YYYY-MM-DD format

        Raises:
            ValidationError: If validation fails
        """
        # Validate quantity
        if not isinstance(quantity, (int, float)):
            raise ValidationError(f"Quantity must be a number, got {type(quantity)}")
        if quantity < MIN_QUANTITY:
            raise ValidationError(f"Quantity must be at least {MIN_QUANTITY}, got {quantity}")
        if quantity > MAX_QUANTITY:
            raise ValidationError(f"Quantity cannot exceed {MAX_QUANTITY}, got {quantity}")

        # Validate purchase price
        if not isinstance(purchase_price, (int, float)):
            raise ValidationError(f"Purchase price must be a number, got {type(purchase_price)}")
        if purchase_price < MIN_PRICE:
            raise ValidationError(f"Purchase price must be at least ₹{MIN_PRICE}, got ₹{purchase_price}")
        if purchase_price > MAX_PRICE:
            raise ValidationError(f"Purchase price cannot exceed ₹{MAX_PRICE}, got ₹{purchase_price}")

        # Validate date format and value
        try:
            date_obj = datetime.strptime(purchase_date, DATE_FORMAT)
            if date_obj > datetime.now():
                raise ValidationError(f"Purchase date cannot be in the future: {purchase_date}")
        except ValueError as e:
            raise ValidationError(f"Invalid date format '{purchase_date}'. Use YYYY-MM-DD") from e

    def add_stock(self, symbol: str, company_name: str, quantity: float,
                  purchase_price: float, purchase_date: str, broker: str = "",
                  cash_invested: float = 0) -> int:
        """
        Add a stock to the portfolio with validation

        Args:
            symbol: Stock ticker symbol
            company_name: Company name
            quantity: Number of shares
            purchase_price: Price per share at purchase
            purchase_date: Purchase date (YYYY-MM-DD)
            broker: Broker name (optional)
            cash_invested: Actual cash invested (optional)

        Returns:
            ID of inserted stock

        Raises:
            ValidationError: If validation fails
            sqlite3.Error: If database operation fails
        """
        # Validate inputs
        if not symbol or not symbol.strip():
            raise ValidationError("Stock symbol cannot be empty")

        self._validate_stock_data(quantity, purchase_price, purchase_date)

        # Calculate cash_invested if not provided
        if cash_invested == 0:
            cash_invested = quantity * purchase_price

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get active user
                active_user = self.get_active_user()
                if not active_user:
                    raise ValidationError("No active user found. Please select a user first.")

                cursor.execute('''
                    INSERT INTO stocks (user_id, symbol, company_name, quantity, purchase_price,
                                      purchase_date, broker, cash_invested, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (active_user['id'], symbol.upper().strip(), company_name, quantity,
                      purchase_price, purchase_date, broker, cash_invested,
                      datetime.now().isoformat()))

                conn.commit()
                stock_id = cursor.lastrowid
                logger.info(f"Added stock: {symbol} (ID: {stock_id}) for user {active_user['username']}")
                return stock_id

        except sqlite3.IntegrityError as e:
            logger.error(f"Database integrity error adding stock {symbol}: {e}")
            raise ValidationError(f"Failed to add stock: {e}") from e
        except sqlite3.Error as e:
            logger.exception(f"Database error adding stock {symbol}: {e}")
            raise

    def get_all_stocks(self) -> List[Dict[str, Any]]:
        """
        Get all stocks for the active user

        Returns:
            List of stock dictionaries

        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                active_user = self.get_active_user()
                if not active_user:
                    logger.warning("No active user found")
                    return []

                cursor.execute('''
                    SELECT s.*, pc.current_price, pc.last_updated
                    FROM stocks s
                    LEFT JOIN price_cache pc ON s.symbol = pc.symbol
                    WHERE s.user_id = ?
                    ORDER BY s.symbol
                ''', (active_user['id'],))

                stocks = [dict(row) for row in cursor.fetchall()]
                logger.debug(f"Retrieved {len(stocks)} stocks for user {active_user['username']}")
                return stocks

        except sqlite3.Error as e:
            logger.exception(f"Error retrieving stocks: {e}")
            raise

    def init_default_users(self):
        """Initialize default users if none exist"""
        try:
            users = self.get_all_users()
            if not users:
                logger.info("No users found, creating default user")
                self.add_user("default", "Default User")
                self.set_active_user("default")
                logger.info("Default user created and activated")
        except Exception as e:
            logger.exception(f"Error initializing default users: {e}")
            raise

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users ORDER BY display_name')
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.exception(f"Error retrieving users: {e}")
            raise

    def get_active_user(self) -> Optional[Dict[str, Any]]:
        """Get the currently active user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE is_active = 1 LIMIT 1')
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.exception(f"Error getting active user: {e}")
            raise

    def add_user(self, username: str, display_name: str) -> int:
        """Add a new user"""
        if not username or not username.strip():
            raise ValidationError("Username cannot be empty")
        if not display_name or not display_name.strip():
            raise ValidationError("Display name cannot be empty")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, display_name, is_active, created_at)
                    VALUES (?, ?, 0, ?)
                ''', (username.lower().strip(), display_name.strip(), datetime.now().isoformat()))
                conn.commit()
                user_id = cursor.lastrowid
                logger.info(f"Added user: {username} (ID: {user_id})")
                return user_id
        except sqlite3.IntegrityError as e:
            logger.error(f"User {username} already exists: {e}")
            raise ValidationError(f"Username '{username}' already exists") from e
        except sqlite3.Error as e:
            logger.exception(f"Error adding user: {e}")
            raise

    def set_active_user(self, username: str):
        """Set the active user"""
        try:
            with self.get_connection() as conn:
                # Deactivate all users
                conn.execute('UPDATE users SET is_active = 0')
                # Activate specified user
                cursor = conn.execute('UPDATE users SET is_active = 1 WHERE username = ?',
                                    (username.lower().strip(),))
                if cursor.rowcount == 0:
                    raise ValidationError(f"User '{username}' not found")
                conn.commit()
                logger.info(f"Set active user: {username}")
        except sqlite3.Error as e:
            logger.exception(f"Error setting active user: {e}")
            raise

    # Additional methods would follow the same pattern...
    # For brevity, I'm showing the pattern with key methods
