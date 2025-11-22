# Database Schema Reference

## Database Files

### ShareProfitTracker
- **File**: `portfolio.db`
- **Location**: Same directory as executable or `ShareProfitTracker/`
- **Type**: SQLite3
- **Encoding**: UTF-8

### ModernShareTracker
- **File**: `unified_portfolio.db`
- **Location**: `ModernShareTracker/`
- **Type**: SQLite3
- **Encoding**: UTF-8

## Complete Schema

### 1. users Table
**Purpose**: Multi-user support with active user tracking

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Columns**:
- `id`: Auto-incrementing primary key
- `username`: Unique username for login
- `display_name`: Display name shown in UI
- `is_active`: Boolean flag for currently active user (only one user is active at a time)
- `created_at`: Timestamp of user creation

**Indexes**: Unique index on username

**Business Logic**:
- Only one user can be active at a time
- Active user is shown in toolbar dropdown
- Each user has separate portfolio, cash, expenses

### 2. stocks Table
**Purpose**: Store portfolio holdings

```sql
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
```

**Columns**:
- `id`: Auto-incrementing primary key
- `user_id`: Foreign key to users table
- `symbol`: Stock ticker symbol (e.g., "RELIANCE.NS", "AAPL")
- `company_name`: Full company name
- `quantity`: Number of shares (REAL to support fractional shares)
- `purchase_price`: Price per share at purchase
- `purchase_date`: Date of purchase (TEXT format: "YYYY-MM-DD")
- `broker`: Broker/platform name (optional)
- `cash_invested`: Actual cash invested (may differ from quantity * price)
- `created_at`: Record creation timestamp

**Constraints**:
- `quantity` must be > 0
- `purchase_price` must be > 0
- Foreign key enforces user existence

**Calculated Fields** (not in database, computed in Python):
- `total_investment`: quantity * purchase_price
- `current_value`: quantity * current_price (from API)
- `profit_loss_amount`: current_value - total_investment
- `profit_loss_percentage`: (profit_loss_amount / total_investment) * 100
- `days_held`: Current date - purchase_date
- `annualized_return`: (profit_loss_percentage / days_held) * 365

### 3. price_cache Table
**Purpose**: Cache stock prices to reduce API calls

```sql
CREATE TABLE IF NOT EXISTS price_cache (
    symbol TEXT PRIMARY KEY,
    current_price REAL,
    last_updated TEXT
);
```

**Columns**:
- `symbol`: Stock symbol (PRIMARY KEY, unique)
- `current_price`: Cached price value
- `last_updated`: Timestamp of last price update

**Usage**:
- Check cache before API call
- Update after successful API fetch
- Invalidate based on time (e.g., 15 minutes)

### 4. cash_transactions Table
**Purpose**: Track cash deposits and withdrawals

```sql
CREATE TABLE IF NOT EXISTS cash_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL, -- 'deposit', 'withdrawal'
    amount REAL NOT NULL,
    description TEXT,
    transaction_date TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

**Columns**:
- `id`: Auto-incrementing primary key
- `user_id`: Foreign key to users
- `transaction_type`: 'deposit' or 'withdrawal'
- `amount`: Transaction amount (positive for both types)
- `description`: Optional transaction description
- `transaction_date`: Date of transaction (YYYY-MM-DD)
- `created_at`: Record creation timestamp

**Constraints**:
- `transaction_type` IN ('deposit', 'withdrawal')
- `amount` must be > 0

**Calculations**:
- Current cash balance = SUM(deposits) - SUM(withdrawals)

### 5. other_expenses Table
**Purpose**: Track non-investment expenses

```sql
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
```

**Columns**:
- `id`: Auto-incrementing primary key
- `user_id`: Foreign key to users
- `category`: Expense category
- `description`: Expense description
- `amount`: Expense amount
- `expense_date`: Date of expense (YYYY-MM-DD)
- `created_at`: Record creation timestamp

**Categories**:
- Electricity
- Rent
- Food
- Transportation
- Healthcare
- Entertainment
- Education
- Shopping
- Other

**Calculations**:
- Total expenses by category
- Monthly expense totals
- Remaining cash = Cash balance - Total expenses

### 6. dividends Table
**Purpose**: Track dividend income

```sql
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
```

**Columns**:
- `id`: Auto-incrementing primary key
- `user_id`: Foreign key to users
- `symbol`: Stock symbol
- `company_name`: Company name
- `dividend_per_share`: Dividend amount per share
- `total_dividend`: Total dividend = dividend_per_share * shares_held
- `shares_held`: Number of shares held on record date
- `ex_dividend_date`: Ex-dividend date (YYYY-MM-DD)
- `payment_date`: Payment date (YYYY-MM-DD)
- `record_date`: Record date (YYYY-MM-DD)
- `dividend_type`: 'regular', 'special', or 'bonus'
- `tax_deducted`: TDS amount (Tax Deducted at Source)
- `net_dividend`: Total dividend - tax_deducted
- `created_at`: Record creation timestamp

**Calculations**:
- Total dividend income by year
- Dividend yield per stock
- Tax summary for ITR filing

### 7. stock_adjustments Table
**Purpose**: Track corporate actions (splits, bonus shares, rights issues)

```sql
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
```

**Columns**:
- `id`: Auto-incrementing primary key
- `symbol`: Stock symbol
- `adjustment_type`: 'split', 'bonus', or 'rights'
- `adjustment_date`: Date of adjustment (YYYY-MM-DD)
- `ratio_from`: Numerator of ratio (e.g., 1 in 1:2 split)
- `ratio_to`: Denominator of ratio (e.g., 2 in 1:2 split)
- `description`: Adjustment description
- `shares_before`: Shares held before adjustment
- `shares_after`: Shares held after adjustment
- `price_before`: Price per share before adjustment
- `price_after`: Price per share after adjustment
- `created_at`: Record creation timestamp

**Examples**:
- **Stock Split 1:2**: ratio_from=1, ratio_to=2, shares_after = shares_before * 2, price_after = price_before / 2
- **Bonus 1:1**: ratio_from=1, ratio_to=1, shares_after = shares_before * 2, price_after = price_before / 2
- **Rights Issue 1:5**: ratio_from=1, ratio_to=5, user can buy 1 share for every 5 held

### 8. price_alerts Table (ModernShareTracker)
**Purpose**: Store price alert configurations

```sql
CREATE TABLE IF NOT EXISTS price_alerts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    condition_value REAL NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    triggered_at TIMESTAMP
);
```

**Columns**:
- `id`: UUID or generated alert ID
- `user_id`: User identifier
- `symbol`: Stock symbol
- `alert_type`: 'price_above', 'price_below', 'percent_change', 'stop_loss', 'target'
- `condition_value`: Threshold value
- `is_active`: Alert is active (disabled after trigger)
- `created_at`: Alert creation timestamp
- `triggered_at`: When alert was triggered

### 9. ai_conversations Table (ModernShareTracker)
**Purpose**: Store AI chatbot conversation history

```sql
CREATE TABLE IF NOT EXISTS ai_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Columns**:
- `id`: Auto-incrementing primary key
- `user_message`: User's question/input
- `ai_response`: AI-generated response
- `created_at`: Conversation timestamp

## Common Queries

### Get Active User
```sql
SELECT * FROM users WHERE is_active = 1 LIMIT 1;
```

### Get User's Portfolio
```sql
SELECT s.*, pc.current_price, pc.last_updated
FROM stocks s
LEFT JOIN price_cache pc ON s.symbol = pc.symbol
WHERE s.user_id = ?
ORDER BY s.created_at DESC;
```

### Calculate Cash Balance
```sql
SELECT 
    COALESCE(SUM(CASE WHEN transaction_type = 'deposit' THEN amount ELSE 0 END), 0) -
    COALESCE(SUM(CASE WHEN transaction_type = 'withdrawal' THEN amount ELSE 0 END), 0) as balance
FROM cash_transactions
WHERE user_id = ?;
```

### Get Tax Report Data
```sql
SELECT 
    symbol,
    company_name,
    quantity,
    purchase_price,
    purchase_date,
    JULIANDAY('now') - JULIANDAY(purchase_date) as days_held,
    CASE 
        WHEN JULIANDAY('now') - JULIANDAY(purchase_date) >= 365 THEN 'LTCG'
        ELSE 'STCG'
    END as tax_type
FROM stocks
WHERE user_id = ?;
```

### Monthly Expense Summary
```sql
SELECT 
    category,
    SUM(amount) as total_amount,
    COUNT(*) as transaction_count
FROM other_expenses
WHERE user_id = ?
    AND strftime('%Y-%m', expense_date) = strftime('%Y-%m', 'now')
GROUP BY category
ORDER BY total_amount DESC;
```

## Database Initialization

### First Run
1. Check if database file exists
2. If not, create with `init_database()`
3. Create all tables with IF NOT EXISTS
4. Create default user if no users exist

### Migration Strategy
- Tables use IF NOT EXISTS (no migration needed for new columns)
- For schema changes, manual migration scripts may be needed
- Backup database before schema changes

## Data Integrity

### Foreign Keys
- Enable foreign keys: `PRAGMA foreign_keys = ON;`
- Enforce user existence before adding stocks
- Cascade deletes not implemented (manual cleanup)

### Constraints
- NOT NULL on critical fields
- UNIQUE constraints on usernames, symbols (in price_cache)
- DEFAULT values for timestamps, booleans
- CHECK constraints for positive amounts (enforced in Python)

### Validation (Python Layer)
- Quantity > 0
- Price > 0
- Valid date formats
- Valid transaction types
- Valid categories
