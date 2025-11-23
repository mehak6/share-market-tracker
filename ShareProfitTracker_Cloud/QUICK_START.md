# 🚀 Quick Start - Using Improved Code

## 5-Minute Integration

### 1. Start Using Logging (Replace ALL print statements)

```python
# Before:
print(f"Error: {error}")
print("Starting application...")

# After:
from utils.logger import get_logger

logger = get_logger(__name__)
logger.error(f"Error: {error}")
logger.info("Starting application...")
```

### 2. Use Constants (No more magic numbers)

```python
# Before:
if quantity < 0.0001:
    raise ValueError("Too small")
tax = profit * 0.156

# After:
from config.constants import MIN_QUANTITY, STCG_RATE

if quantity < MIN_QUANTITY:
    raise ValidationError(f"Quantity below {MIN_QUANTITY}")
tax = profit * STCG_RATE
```

### 3. Enable Database Safety (One-line change)

```python
# In your existing database.py, update get_connection():

def get_connection(self) -> sqlite3.Connection:
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
    # Add these two lines:
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA journal_mode = WAL')
    return conn
```

**That's it! You're already 50% improved!** 🎉

---

## Testing Your Changes

### Run Tests
```bash
# Install pytest
pip install pytest

# Run tests
python -m pytest ShareProfitTracker/tests/ -v
```

### Expected Output
```
tests/test_models.py::TestStockModel::test_valid_stock_creation PASSED
tests/test_models.py::TestStockModel::test_invalid_quantity PASSED
...
==================== 25 passed in 1.2s ====================
```

---

## Full Migration (Choose What You Need)

### Option A: Keep Current Code, Add Improvements
Use improved versions for **new features only**:
```python
# New feature using improved code
from data.models_improved import Stock
from utils.logger import get_logger

logger = get_logger(__name__)
```

### Option B: Gradual Replacement
Replace one module at a time:

**Week 1: Models**
```python
# Change in your imports
from data.models_improved import Stock, PortfolioSummary
```

**Week 2: Database**
```python
from data.database_improved import DatabaseManager, ValidationError
```

**Week 3: Price Fetcher**
```python
from services.price_fetcher_improved import PriceFetcher
```

### Option C: Complete Migration
See `IMPROVEMENTS_GUIDE.md` for detailed steps.

---

## Common Patterns

### Pattern 1: Logging Everything
```python
from utils.logger import get_logger

logger = get_logger(__name__)

def my_function():
    logger.info("Function started")
    try:
        # Your code
        logger.debug(f"Processing {data}")
        result = process(data)
        logger.info("Function completed successfully")
        return result
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise
```

### Pattern 2: Using Constants
```python
from config.constants import (
    MIN_QUANTITY, MAX_QUANTITY,
    MIN_PRICE, MAX_PRICE,
    STCG_RATE, LTCG_RATE,
    LTCG_HOLDING_PERIOD_DAYS
)

def validate_stock(quantity, price, days_held):
    if not MIN_QUANTITY <= quantity <= MAX_QUANTITY:
        raise ValidationError(f"Invalid quantity: {quantity}")

    if not MIN_PRICE <= price <= MAX_PRICE:
        raise ValidationError(f"Invalid price: {price}")

    tax_rate = LTCG_RATE if days_held >= LTCG_HOLDING_PERIOD_DAYS else STCG_RATE
    return tax_rate
```

### Pattern 3: Safe Validation
```python
from data.models_improved import Stock, StockValidationError

def add_stock_safely(symbol, quantity, price, date):
    try:
        stock = Stock(
            symbol=symbol,
            company_name="Company Name",
            quantity=quantity,
            purchase_price=price,
            purchase_date=date
        )
        # If we reach here, validation passed!
        return stock
    except StockValidationError as e:
        logger.error(f"Invalid stock data: {e}")
        messagebox.showerror("Validation Error", str(e))
        return None
```

### Pattern 4: Background Tasks
```python
from utils.thread_safe_queue import BackgroundTaskManager, TaskStatus

task_manager = BackgroundTaskManager()

def refresh_prices_safely():
    def fetch_all_prices():
        # Long-running task
        prices = price_fetcher.get_multiple_prices(symbols)
        return prices

    def on_complete(result):
        if result.status == TaskStatus.COMPLETED:
            self.update_ui(result.result)
            logger.info("Prices updated successfully")
        else:
            logger.error(f"Price fetch failed: {result.error_message}")
            messagebox.showerror("Error", "Failed to fetch prices")

    task_id = task_manager.submit_task(
        fetch_all_prices,
        callback=on_complete
    )
```

---

## Cheat Sheet

### Import Statement Quick Reference

```python
# Logging
from utils.logger import get_logger
logger = get_logger(__name__)

# Constants
from config.constants import (
    STCG_RATE, LTCG_RATE,
    MIN_QUANTITY, MIN_PRICE,
    API_RATE_LIMIT_SECONDS
)

# Improved Models
from data.models_improved import (
    Stock, PortfolioSummary,
    StockValidationError
)

# Improved Database
from data.database_improved import (
    DatabaseManager,
    ValidationError
)

# Improved Price Fetcher
from services.price_fetcher_improved import (
    PriceFetcher,
    PriceFetchError
)

# Thread Safety
from utils.thread_safe_queue import (
    BackgroundTaskManager,
    TaskStatus,
    TaskResult
)
```

### Error Handling Quick Reference

```python
# Catch specific exceptions
try:
    # Database operation
    db.add_stock(...)
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    messagebox.showwarning("Invalid Data", str(e))
except sqlite3.IntegrityError as e:
    logger.error(f"Database integrity error: {e}")
    messagebox.showerror("Database Error", "Duplicate or constraint violation")
except sqlite3.Error as e:
    logger.exception(f"Database error: {e}")
    messagebox.showerror("Error", "Database operation failed")
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    messagebox.showerror("Error", "An unexpected error occurred")
```

---

## Troubleshooting

### Problem: ImportError
```python
# Solution: Check your sys.path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### Problem: Tests Not Running
```bash
# Install test dependencies
pip install -r ShareProfitTracker/requirements-dev.txt

# Run from project root
python -m pytest ShareProfitTracker/tests/ -v
```

### Problem: Logs Not Appearing
```python
# Initialize root logger at application start
from utils.logger import LoggerSetup
LoggerSetup.setup_logger('ShareTracker', logging.INFO)
```

---

## Performance Tips

1. **Logging**: Use appropriate log levels
   - `DEBUG`: Detailed diagnostic info (disabled in production)
   - `INFO`: General informational messages
   - `WARNING`: Warning messages
   - `ERROR`: Error messages
   - `CRITICAL`: Critical errors

2. **Validation**: Fail fast - validate at entry points

3. **Threading**: Use task manager for all background operations

4. **Database**: PRAGMA WAL mode improves concurrent access

---

## Next Steps

1. ✅ Replace `print()` with `logger.*()`
2. ✅ Import constants instead of hardcoding
3. ✅ Enable PRAGMA in database connection
4. ✅ Run tests to ensure nothing broke
5. ✅ Gradually adopt improved versions

**Time investment**: 5 minutes to start, 1-2 hours for full migration

**Benefit**: Production-ready, maintainable, professional code! 🚀

---

## Resources

- Full guide: `IMPROVEMENTS_GUIDE.md`
- Summary: `IMPROVEMENTS_SUMMARY.md`
- Code review: See root directory
- Tests: `ShareProfitTracker/tests/`

**Questions?** Check the logs: `ShareProfitTracker/logs/sharetracker.log`
