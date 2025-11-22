# Code Conventions and Patterns

## Programming Language
- **Primary Language**: Python 3.9+
- **Type Hints**: Extensive use of typing module (List, Dict, Optional, Any)
- **Async/Await**: Used in database and price fetching operations

## Code Organization

### Import Conventions
```python
# Standard library imports first
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict

# Third-party imports
import yfinance as yf
import pandas as pd
import numpy as np

# Local imports
from data.models import Stock, PortfolioSummary
from services.price_fetcher import PriceFetcher
from utils.config import AppConfig
```

### Path Handling
```python
# Dynamic path resolution for imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### Try-Except for Imports
```python
try:
    from gui.main_window import MainWindow
except ImportError:
    from .main_window import MainWindow  # Relative import fallback
```

## Naming Conventions

### Classes
- **Pattern**: PascalCase
- **Examples**: `MainWindow`, `DatabaseManager`, `PriceFetcher`, `PortfolioCalculator`
- **Dataclasses**: `@dataclass` decorator for data models

### Functions and Methods
- **Pattern**: snake_case
- **Examples**: `get_current_price()`, `calculate_portfolio_summary()`, `load_portfolio()`
- **Private methods**: Prefix with underscore `_rate_limit()`
- **Async methods**: Prefix with `async def`

### Variables
- **Pattern**: snake_case
- **Examples**: `db_path`, `last_update_time`, `portfolio_summary`
- **Constants**: UPPER_SNAKE_CASE in config files
- **Class attributes**: snake_case with self prefix

### Files and Modules
- **Pattern**: snake_case
- **Examples**: `main_window.py`, `price_fetcher.py`, `stock_symbols.py`

## Data Models

### Dataclass Usage
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Stock:
    symbol: str
    company_name: str
    quantity: float
    purchase_price: float
    purchase_date: str
    broker: str = ""
    cash_invested: float = 0
    id: Optional[int] = None
    current_price: Optional[float] = None
    
    @property
    def total_investment(self) -> float:
        return self.quantity * self.purchase_price
    
    @property
    def profit_loss_amount(self) -> float:
        return self.current_value - self.total_investment
```

### Property Decorators
- Extensive use of `@property` for calculated fields
- Keeps data models clean
- Examples: `total_investment`, `profit_loss_percentage`, `days_held`

## Database Patterns

### Connection Management
```python
def get_connection(self) -> sqlite3.Connection:
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row  # Dict-like row access
    return conn
```

### Context Manager Usage
```python
with self.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
```

### Parameterized Queries
```python
# ALWAYS use parameter substitution to prevent SQL injection
cursor.execute(
    'INSERT INTO stocks (symbol, quantity, price) VALUES (?, ?, ?)',
    (symbol, quantity, price)
)
```

### Row Factory
```python
conn.row_factory = sqlite3.Row  # Enables dict-like access
row = cursor.fetchone()
value = row['column_name']  # Instead of row[0]
```

## Error Handling Patterns

### Try-Except Blocks
```python
try:
    # Operation that might fail
    price = self.fetch_price(symbol)
except Exception as e:
    print(f"Error fetching price for {symbol}: {e}")
    return None
```

### Graceful Degradation
```python
try:
    import yfinance as yf
    MOCK_MODE = False
except ImportError:
    import mock_yfinance as yf
    MOCK_MODE = True
    print("Warning: Using mock data")
```

### Return None on Error
```python
def get_current_price(self, symbol: str) -> Optional[float]:
    try:
        # Fetch price
        return price
    except Exception as e:
        print(f"Error: {e}")
        return None  # Explicit None return
```

## GUI Patterns

### Tkinter Widget Creation
```python
# Frame creation
frame = tk.Frame(parent, bg='white')
frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

# Grid weight configuration
frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)

# Widget packing
label = tk.Label(frame, text="Text", font=('Arial', 12))
label.pack(side=tk.LEFT, padx=5)
```

### Dialog Pattern
```python
class CustomDialog(tk.Toplevel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.title("Dialog Title")
        self.geometry("600x400")
        self.transient(parent)  # Modal dialog
        self.grab_set()  # Block parent interaction
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create UI elements
        pass
```

### Callback Pattern
```python
# Button with command
button = tk.Button(frame, text="Click", command=self.on_click)

# Event binding
widget.bind('<Return>', self.on_enter)

# Lambda for parameters
button = tk.Button(text="Delete", command=lambda: self.delete_item(item_id))
```

## Async Patterns

### AsyncDatabaseManager
```python
import aiosqlite

class AsyncDatabaseManager:
    async def get_connection(self):
        return await aiosqlite.connect(self.db_path)
    
    async def execute_query(self, query, params=None):
        async with self.get_connection() as conn:
            async with conn.execute(query, params or []) as cursor:
                result = await cursor.fetchall()
                await conn.commit()
                return result
```

### Async Price Fetching
```python
async def get_multiple_prices_ultra_fast(symbols: List[str]) -> Dict[str, float]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_price(symbol)) for symbol in symbols]
    return {symbol: task.result() for symbol, task in zip(symbols, tasks)}
```

### Threading for UI Responsiveness
```python
def refresh_prices(self):
    self.is_updating = True
    
    def update_thread():
        try:
            prices = self.fetch_all_prices()
            self.root.after(0, lambda: self.update_ui(prices))
        finally:
            self.is_updating = False
    
    thread = threading.Thread(target=update_thread, daemon=True)
    thread.start()
```

## Configuration Patterns

### AppConfig Class
```python
class AppConfig:
    # Application Info
    APP_NAME = "Share Profit Tracker"
    APP_VERSION = "1.0"
    
    # Window Settings
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    
    # Paths
    @staticmethod
    def get_database_path():
        return os.path.join(os.getcwd(), 'portfolio.db')
    
    @staticmethod
    def ensure_directories():
        os.makedirs('backups', exist_ok=True)
```

## Stock Symbol Management

### Database Loading Pattern
```python
def load_massive_stock_database() -> Dict[str, str]:
    """Load with multiple fallbacks"""
    try:
        # Try primary database
        with open('massive_stocks_2000plus.json', 'r') as f:
            data = json.load(f)
            return data['nse_stocks']
    except:
        try:
            # Try secondary database
            with open('ultra_comprehensive_stocks.json', 'r') as f:
                return json.load(f)['nse_stocks']
        except:
            # Final fallback
            return get_popular_fallback_stocks()
```

### Search Implementation
```python
def search_stocks(query: str, limit: int = 10):
    query = query.upper()
    matches = []
    
    # Exact symbol matches first
    for symbol, company in ALL_STOCKS.items():
        if symbol.upper().startswith(query):
            matches.append((symbol, company))
    
    # Then company name matches
    for symbol, company in ALL_STOCKS.items():
        if query in company.upper() and (symbol, company) not in matches:
            matches.append((symbol, company))
    
    return matches[:limit]
```

## Formatting Utilities

### Currency Formatting
```python
@staticmethod
def format_currency(amount: float) -> str:
    return f"₹{amount:,.2f}"  # Indian Rupee with comma separators
```

### Percentage Formatting
```python
@staticmethod
def format_percentage(percentage: float) -> str:
    return f"{percentage:+.2f}%"  # + sign for positive values
```

### Color by Value
```python
@staticmethod
def get_profit_loss_color(amount: float) -> str:
    if amount > 0:
        return "green"
    elif amount < 0:
        return "red"
    else:
        return "black"
```

## Testing Patterns

### Test File Naming
- Pattern: `test_*.py`
- Examples: `test_phase1.py`, `test_enhanced_notifications.py`

### Mock Data
```python
# Mock yfinance for testing
class MockTicker:
    def __init__(self, symbol):
        self.symbol = symbol
        self.info = {
            'currentPrice': self._get_mock_price(),
            'longName': self._get_mock_name()
        }
```

## Documentation

### Docstrings
```python
def analyze_portfolio(self, portfolio_data: Dict) -> Dict[str, Any]:
    """
    Analyze user's portfolio and generate insights
    
    Args:
        portfolio_data: Dictionary containing portfolio stocks
        
    Returns:
        Dict with portfolio metrics, risk assessment, and recommendations
    """
```

### Module-Level Documentation
```python
"""
Stock Symbol Database Management

Provides comprehensive Indian stock symbol database with fallback mechanisms.
Supports 2000+ NSE/BSE stocks with company names.
"""
```

## Performance Optimization

### Rate Limiting
```python
def _rate_limit(self):
    current_time = time.time()
    time_since_last = current_time - self.last_request_time
    if time_since_last < self.min_request_interval:
        time.sleep(self.min_request_interval - time_since_last)
    self.last_request_time = time.time()
```

### Caching
```python
# Database-backed price cache
CREATE TABLE price_cache (
    symbol TEXT PRIMARY KEY,
    current_price REAL,
    last_updated TEXT
)

# Check cache before API call
def get_current_price(self, symbol: str) -> Optional[float]:
    cached = self.get_from_cache(symbol)
    if cached and not self.is_cache_stale(cached):
        return cached['price']
    
    return self.fetch_from_api(symbol)
```

### Batch Operations
```python
def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
    # Batch fetch instead of individual requests
    symbols_str = " ".join(symbols)
    tickers = yf.Tickers(symbols_str)
    
    return {symbol: self.extract_price(tickers.tickers[symbol]) 
            for symbol in symbols}
```
