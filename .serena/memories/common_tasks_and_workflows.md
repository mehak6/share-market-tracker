# Common Tasks and Workflows

## User Workflows

### 1. First-Time Application Launch
**Steps**:
1. Application checks if database exists
2. If not, runs `init_database()` to create schema
3. Creates default user if no users exist
4. Sets default user as active
5. Displays empty portfolio
6. User can start adding stocks

**Code Flow**:
```
main.py
  └─> MainWindow.__init__()
      └─> DatabaseManager.__init__()
          └─> init_database()
              └─> Create all tables
              └─> Check for users
                  └─> Create default user if needed
```

### 2. Adding a New Stock
**User Actions**:
1. Click "Add Stock" button
2. Type stock symbol/name in autocomplete field
3. Select from suggestions
4. Enter quantity, purchase price, purchase date
5. Optionally enter broker and cash invested
6. Click "Save"

**Code Flow**:
```
MainWindow.add_stock()
  └─> AddStockDialog(parent, db_manager, callback)
      └─> AutocompleteEntry widget
          └─> Search stock symbols on keystroke
          └─> Display matching symbols
      └─> Validate inputs
      └─> db_manager.add_stock(user_id, stock_data)
          └─> INSERT INTO stocks
      └─> callback() - refresh main window
```

**Validation**:
- Symbol must exist in database
- Quantity > 0
- Purchase price > 0
- Date format: YYYY-MM-DD
- Date not in future

### 3. Refreshing Stock Prices
**User Actions**:
1. Click "Refresh Prices" button
2. Wait for progress indicator
3. View updated prices and profit/loss

**Code Flow**:
```
MainWindow.refresh_prices()
  └─> Start background thread (to avoid UI freeze)
      └─> Get all unique symbols from portfolio
      └─> PriceFetcher.get_multiple_prices(symbols)
          └─> Batch fetch from Yahoo Finance
          └─> Update price_cache table
      └─> Update UI via root.after(0, callback)
          └─> Refresh portfolio display
          └─> Update summary metrics
          └─> Update last_update_time
```

**Threading Pattern**:
```python
def refresh_prices(self):
    self.is_updating = True
    
    def update_thread():
        try:
            # Fetch prices in background
            prices = self.price_fetcher.get_multiple_prices(symbols)
            # Update database
            self.update_price_cache(prices)
            # Update UI in main thread
            self.root.after(0, lambda: self.refresh_display(prices))
        finally:
            self.is_updating = False
    
    thread = threading.Thread(target=update_thread, daemon=True)
    thread.start()
```

### 4. Viewing Tax Report
**User Actions**:
1. Click "Tax Report" button
2. View holdings classified by STCG/LTCG
3. See potential tax liability
4. Export to CSV if needed

**Code Flow**:
```
MainWindow.show_tax_report()
  └─> TaxReportDialog(parent, db_manager, user_id)
      └─> Fetch all stocks for user
      └─> Calculate days held for each stock
      └─> Classify as STCG (< 365 days) or LTCG (≥ 365 days)
      └─> Calculate potential gains
      └─> Calculate tax liability
          └─> STCG: gain × 15.6%
          └─> LTCG: (gain - ₹1L exemption) × 10.4%
      └─> Display in categorized tables
      └─> Show summary totals
```

### 5. Managing Cash Transactions
**User Actions**:
1. Click "Cash I Have" button
2. View current balance
3. Add deposit or withdrawal
4. View transaction history

**Code Flow**:
```
MainWindow.manage_cash()
  └─> CashManagementDialog(parent, db_manager, user_id)
      └─> Calculate current balance
          └─> SUM deposits - SUM withdrawals
      └─> Display transaction list
      └─> Add Transaction
          └─> Validate amount > 0
          └─> INSERT INTO cash_transactions
          └─> Refresh balance display
```

### 6. Tracking Expenses
**User Actions**:
1. Click "Other Funds" button
2. Select category
3. Enter description and amount
4. View expense breakdown by category

**Code Flow**:
```
MainWindow.manage_expenses()
  └─> ExpensesDialog(parent, db_manager, user_id)
      └─> Load expenses by category
      └─> Calculate monthly totals
      └─> Display category breakdown
      └─> Add Expense
          └─> Validate category, amount
          └─> INSERT INTO other_expenses
          └─> Update category totals
```

### 7. Recording Dividends
**User Actions**:
1. Click "Dividends" (if available)
2. Select stock from portfolio
3. Enter dividend per share
4. Enter dates (ex-dividend, payment, record)
5. Enter tax deducted
6. Save

**Code Flow**:
```
MainWindow.add_dividend()
  └─> DividendDialog(parent, db_manager, user_id)
      └─> Load portfolio stocks for dropdown
      └─> Auto-calculate total dividend
          └─> dividend_per_share × shares_held
      └─> Calculate net dividend
          └─> total_dividend - tax_deducted
      └─> INSERT INTO dividends
```

### 8. Exporting Portfolio Data
**User Actions**:
1. Click "Export" button
2. Choose export type (Portfolio/Tax/Cash)
3. Select format (CSV/Excel)
4. Choose save location
5. Confirm export

**Code Flow**:
```
MainWindow.export_portfolio()
  └─> ExportDialog(parent, data_type, format)
      └─> Gather data from database
      └─> Format data for export
      └─> If CSV:
          └─> FileHelper.export_to_csv(data, filename)
      └─> If Excel:
          └─> FileHelper.export_to_excel(data, filename)
      └─> Show success message
```

## Developer Workflows

### 1. Adding a New Feature
**Steps**:
1. Identify the layer (GUI, Service, Data)
2. Create necessary files
3. Update imports
4. Add database schema changes if needed
5. Implement business logic
6. Add UI components
7. Test locally
8. Update build scripts if new dependencies

**Example - Adding a New Service**:
```python
# 1. Create service file
# services/new_feature_service.py

class NewFeatureService:
    def __init__(self):
        pass
    
    def perform_action(self, data):
        # Business logic
        pass

# 2. Import in main window
# gui/main_window.py
from services.new_feature_service import NewFeatureService

# 3. Initialize in MainWindow
def __init__(self):
    self.new_service = NewFeatureService()

# 4. Create UI button
def create_widgets(self):
    button = tk.Button(
        frame, 
        text="New Feature",
        command=self.use_new_feature
    )
    
# 5. Implement callback
def use_new_feature(self):
    result = self.new_service.perform_action(self.data)
    self.update_display(result)
```

### 2. Adding a New Stock Symbol Source
**Steps**:
1. Create JSON file with stock data
2. Update `massive_stock_symbols.py` to load it
3. Add fallback logic
4. Test autocomplete
5. Update build spec to include JSON

**Example**:
```python
# data/massive_stock_symbols.py

def load_massive_stock_database() -> Dict[str, str]:
    try:
        # Try new database
        new_db_path = os.path.join(os.path.dirname(__file__), 'new_stocks.json')
        if os.path.exists(new_db_path):
            with open(new_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['stocks']
        
        # Fall back to existing
        return load_existing_database()
    except Exception as e:
        print(f"Error: {e}")
        return get_popular_fallback_stocks()
```

### 3. Modifying Database Schema
**Steps**:
1. Update schema in `database.py`
2. Create migration script (if needed)
3. Test with fresh database
4. Test with existing database
5. Update models.py if data classes affected
6. Update queries that use the table

**Example - Adding a Column**:
```python
# database.py
def init_database(self):
    # Add new column to existing table
    with self.get_connection() as conn:
        try:
            conn.execute('''
                ALTER TABLE stocks 
                ADD COLUMN new_field TEXT DEFAULT '';
            ''')
        except sqlite3.OperationalError:
            # Column already exists
            pass
```

### 4. Building Executable
**Steps**:
1. Update version in `utils/config.py`
2. Update requirements.txt if new dependencies
3. Test locally: `python main.py`
4. Clean cache: `rmdir /s /q __pycache__`
5. Run build script: `build_ultimate_complete.bat`
6. Test executable
7. Verify file size
8. Test on clean machine (if possible)

**Checklist**:
- [ ] Version number updated
- [ ] All dependencies in requirements.txt
- [ ] Build script selects correct main file
- [ ] Hidden imports in spec file
- [ ] Data files included in spec
- [ ] Tested locally before building
- [ ] Executable runs without Python installed
- [ ] Database creates on first run
- [ ] No import errors
- [ ] File size acceptable

### 5. Debugging Price Fetch Issues
**Common Issues and Solutions**:

**Issue**: No prices fetched
```python
# Solution: Check mock mode
if MOCK_MODE:
    print("Running in mock mode - install yfinance")
else:
    # Check symbol format
    print(f"Fetching: {symbol}")
    # Add .NS for Indian stocks
    if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
        symbol += '.NS'
```

**Issue**: Slow price updates
```python
# Solution: Use batch fetching
# Instead of:
for symbol in symbols:
    price = fetch_price(symbol)  # Slow, many API calls

# Use:
prices = fetch_multiple_prices(symbols)  # Fast, one API call
```

**Issue**: API rate limiting
```python
# Solution: Add delays and caching
def get_price_with_cache(symbol):
    # Check cache first
    cached = get_from_cache(symbol)
    if cached and not is_stale(cached):
        return cached['price']
    
    # Rate limit
    time.sleep(0.1)
    
    # Fetch and cache
    price = fetch_from_api(symbol)
    save_to_cache(symbol, price)
    return price
```

## Error Recovery Workflows

### 1. Database Corruption
**Recovery Steps**:
1. Export data to CSV (if database accessible)
2. Rename corrupted database: `portfolio.db.corrupt`
3. Restart application (creates fresh database)
4. Import data from CSV
5. Verify data integrity

### 2. Import Errors at Runtime
**Diagnosis**:
```python
# Add debug prints
try:
    from gui.main_window import MainWindow
    print("✓ Main window imported")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
```

**Common Fixes**:
- Check sys.path includes project root
- Verify __init__.py exists in packages
- Check for circular imports
- Verify file names match imports

### 3. Price Fetch Failures
**Fallback Sequence**:
1. Try primary API (Yahoo Finance)
2. Check cache for recent price
3. Try NSE Python API (if Indian stock)
4. Return None and log error
5. Display "N/A" in UI

**Implementation**:
```python
def get_price_with_fallbacks(symbol: str) -> Optional[float]:
    # Try Yahoo Finance
    try:
        price = yf_fetch(symbol)
        if price:
            return price
    except:
        pass
    
    # Try cache
    cached = get_cached_price(symbol)
    if cached:
        print(f"Using cached price for {symbol}")
        return cached
    
    # Try NSE (for .NS symbols)
    if symbol.endswith('.NS'):
        try:
            price = nse_fetch(symbol.replace('.NS', ''))
            if price:
                return price
        except:
            pass
    
    # All failed
    print(f"All price sources failed for {symbol}")
    return None
```

## Testing Workflows

### 1. Manual Testing Checklist
**Before Release**:
- [ ] Add stock (valid symbol)
- [ ] Add stock (invalid symbol - should error)
- [ ] Edit existing stock
- [ ] Delete stock
- [ ] Refresh prices
- [ ] View tax report
- [ ] Add cash transaction
- [ ] Add expense
- [ ] Export to CSV
- [ ] Switch users
- [ ] Dark/Light theme toggle
- [ ] Search stocks
- [ ] Sort portfolio
- [ ] Close and reopen (data persists)

### 2. Automated Testing
**Test Files**:
- `test_phase1.py` - Basic functionality
- `test_enhanced_notifications.py` - Notifications
- `test_2000plus_coverage.py` - Stock database coverage
- `test_comprehensive_coverage.py` - Comprehensive tests

**Running Tests**:
```bash
cd ShareProfitTracker
python test_phase1.py
python test_comprehensive_coverage.py
```

### 3. Build Testing
**Post-Build Verification**:
1. Run executable on build machine
2. Check file size (should be 12-15 MB)
3. Test on machine without Python
4. Verify database creation
5. Test all core features
6. Check for console errors
7. Test price refresh
8. Verify exports work

## Maintenance Workflows

### 1. Updating Stock Database
**Steps**:
1. Fetch latest stock list from NSE/BSE
2. Format as JSON
3. Update JSON file in `data/`
4. Test autocomplete
5. Rebuild executable
6. Update version number

### 2. Dependency Updates
**Steps**:
1. Check for updates: `pip list --outdated`
2. Test updates locally
3. Update requirements.txt
4. Test all features
5. Update build scripts if needed
6. Rebuild and test executable

### 3. Database Schema Evolution
**Safe Migration Pattern**:
```python
def migrate_database(conn):
    # Get current schema version
    version = get_schema_version(conn)
    
    if version < 2:
        # Add new column
        conn.execute('ALTER TABLE stocks ADD COLUMN sector TEXT')
        set_schema_version(conn, 2)
    
    if version < 3:
        # Add new table
        conn.execute('CREATE TABLE portfolio_snapshots (...)')
        set_schema_version(conn, 3)
```
