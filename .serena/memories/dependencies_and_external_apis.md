# Dependencies and External APIs

## Python Dependencies

### Core Requirements (requirements.txt)
Located in both `ShareProfitTracker/` and `ModernShareTracker/`

```
yfinance>=0.2.18          # Yahoo Finance API wrapper
nsepython>=2.97           # NSE India data
nsetools>=2.0.1          # NSE tools (alternative)
pandas>=2.0.0            # Data analysis library
numpy>=1.24.0            # Numerical computing
openpyxl>=3.1.0          # Excel file operations
aiosqlite>=0.19.0        # Async SQLite support
tkcalendar>=1.6.1        # Calendar widget for Tkinter
beautifulsoup4>=4.12.0   # HTML parsing
lxml>=4.9.0              # XML/HTML parser
requests>=2.31.0         # HTTP library
```

### Optional Dependencies
```
openai                   # AI chatbot integration (optional)
websocket-client         # WebSocket for real-time data (optional)
pyinstaller             # Build tool (development only)
```

### Built-in Dependencies (No installation needed)
- **tkinter**: GUI framework (comes with Python)
- **sqlite3**: Database (comes with Python)
- **asyncio**: Async programming (comes with Python)
- **threading**: Multi-threading support (comes with Python)
- **json**: JSON handling (comes with Python)
- **csv**: CSV file operations (comes with Python)
- **datetime**: Date/time handling (comes with Python)
- **os, sys**: System operations (comes with Python)

## External APIs

### 1. Yahoo Finance API (via yfinance)

#### Purpose
- Real-time and historical stock price data
- Company information
- Market data

#### Usage in Code
```python
import yfinance as yf

# Single stock
ticker = yf.Ticker("RELIANCE.NS")
info = ticker.info
current_price = info['currentPrice']
company_name = info['longName']

# Multiple stocks
tickers = yf.Tickers("RELIANCE.NS TCS.NS INFY.NS")
for symbol, ticker in tickers.tickers.items():
    price = ticker.info['currentPrice']
```

#### Key Features Used
- `Ticker.info`: Stock information dictionary
- Price fields: `currentPrice`, `regularMarketPrice`, `previousClose`
- Company fields: `longName`, `shortName`
- Batch fetching with `Tickers()`

#### Rate Limiting
- Custom rate limiting implemented in `PriceFetcher._rate_limit()`
- Minimum 100ms between requests (`min_request_interval = 0.1`)
- Batch fetching to reduce API calls

#### Fallback Mechanism
- Mock data mode if yfinance unavailable
- `MOCK_MODE` flag tracks availability
- `mock_yfinance.py` provides test data

#### Stock Symbol Format
- **Indian stocks**: Add `.NS` suffix (NSE) or `.BO` (BSE)
  - Example: `RELIANCE.NS`, `TCS.NS`
- **US stocks**: No suffix needed
  - Example: `AAPL`, `GOOGL`, `MSFT`

#### Known Limitations
- Free tier has rate limits
- Some stocks may have delayed data
- Weekend/holiday data may be stale
- International stocks have varying availability

### 2. NSE Python API (nsepython)

#### Purpose
- NSE India specific data
- Corporate actions
- Real-time quotes
- Advanced market data

#### Usage in Code
```python
from nsepython import nsefetch

# Fetch NSE data
data = nsefetch('https://www.nseindia.com/api/quote-equity?symbol=RELIANCE')

# Corporate actions
corporate_actions = get_corporate_actions('RELIANCE')
```

#### Key Features
- Direct NSE API access
- Corporate action data (splits, bonuses, dividends)
- More reliable for Indian stocks
- Real-time data during market hours

#### Integration Points
- `services/comprehensive_nse_bse_fetcher.py`
- `services/corporate_actions_fetcher.py`
- `services/complete_stock_fetcher.py`

### 3. NSE Tools (nsetools)

#### Purpose
- Alternative NSE data source
- Stock listings
- Index data

#### Usage
```python
from nsetools import Nse

nse = Nse()
all_stocks = nse.get_stock_codes()  # Get all NSE stock codes
```

## Data Sources

### Stock Symbol Databases

#### 1. Built-in Databases (Python files)
- **stock_symbols.py**: ~50 popular stocks
- **enhanced_stock_symbols.py**: ~200 stocks
- **massive_stock_symbols.py**: Loader for JSON databases

#### 2. JSON Databases (Data files)
- **massive_stocks_2000plus.json**: 2000+ stocks
- **ultra_comprehensive_stocks.json**: Ultra comprehensive list
- **complete_indian_stocks.json**: Complete Indian stocks
- **comprehensive_indian_stocks.json**: Comprehensive list (ModernShareTracker)
- **comprehensive_indian_stocks_2000plus.json**: Extended 2000+ (ModernShareTracker)

#### Structure
```json
{
  "nse_stocks": {
    "RELIANCE": "Reliance Industries Limited",
    "TCS": "Tata Consultancy Services Limited",
    "INFY": "Infosys Limited"
  },
  "bse_stocks": {
    "500325": "Reliance Industries Limited"
  },
  "metadata": {
    "total_count": 2000,
    "last_updated": "2024-09-01"
  }
}
```

### Price Caching

#### Database Table
```sql
CREATE TABLE price_cache (
    symbol TEXT PRIMARY KEY,
    current_price REAL,
    last_updated TEXT
)
```

#### Purpose
- Reduce API calls
- Improve performance
- Offline price viewing

#### Cache Strategy
- Check cache first
- Fetch from API if cache is stale
- Update cache after successful fetch
- Cache timeout: Configurable (typically 15 minutes during market hours)

## API Integration Patterns

### Error Handling
```python
def get_current_price(self, symbol: str) -> Optional[float]:
    try:
        self._rate_limit()
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Try multiple price fields
        price_fields = ['currentPrice', 'regularMarketPrice', 'previousClose']
        for field in price_fields:
            if field in info and info[field] is not None:
                return float(info[field])
        
        return None
        
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None
```

### Batch Fetching
```python
def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Optional[float]]:
    prices = {}
    
    try:
        # Batch request
        symbols_str = " ".join(symbols)
        tickers = yf.Tickers(symbols_str)
        
        for symbol in symbols:
            prices[symbol] = self.extract_price(tickers.tickers[symbol])
            
    except Exception as e:
        # Fallback to individual requests
        for symbol in symbols:
            prices[symbol] = self.get_current_price(symbol)
            time.sleep(0.1)
    
    return prices
```

### Async Implementation
```python
async def get_multiple_prices_ultra_fast(symbols: List[str]) -> Dict[str, float]:
    """Ultra-fast async price fetching"""
    
    async def fetch_single(symbol: str) -> tuple:
        try:
            # Async API call
            price = await async_fetch_price(symbol)
            return (symbol, price)
        except:
            return (symbol, None)
    
    # Concurrent fetching
    tasks = [fetch_single(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks)
    
    return dict(results)
```

## Data Export

### CSV Export
```python
import csv

def export_to_csv(data: List[Dict], filename: str):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        if not data:
            return
        
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
```

### Excel Export
```python
from openpyxl import Workbook

def export_to_excel(data: List[Dict], filename: str):
    wb = Workbook()
    ws = wb.active
    
    # Headers
    headers = list(data[0].keys())
    ws.append(headers)
    
    # Data rows
    for row in data:
        ws.append(list(row.values()))
    
    wb.save(filename)
```

## Third-Party Integration Points

### Email Notifications (Optional)
```python
import smtplib
from email.mime.text import MIMEText

def send_alert_email(to: str, subject: str, body: str):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'alerts@sharetracker.com'
    msg['To'] = to
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('user', 'password')
        server.send_message(msg)
```

### Desktop Notifications (Windows)
```python
from plyer import notification  # Optional dependency

def show_notification(title: str, message: str):
    notification.notify(
        title=title,
        message=message,
        app_name='Share Profit Tracker',
        timeout=10
    )
```

## API Authentication

### No Authentication Required
- Yahoo Finance API: Free, no API key needed
- NSE Python: Free, no authentication
- NSE Tools: Free, no authentication

### Optional Authentication
- OpenAI API: Requires API key for AI chatbot
  ```python
  import openai
  openai.api_key = 'your-api-key-here'
  ```

## Network Requirements

### Internet Connection
- **Required for**: Price updates, stock symbol search
- **Not required for**: Viewing cached data, portfolio management
- **Graceful degradation**: Falls back to cached prices when offline

### Firewall/Proxy
- HTTP/HTTPS outbound connections required
- Ports: 80 (HTTP), 443 (HTTPS)
- No special firewall rules needed

### Data Usage
- Price update: ~1-5 KB per stock
- Batch fetch (100 stocks): ~100-500 KB
- Minimal bandwidth requirements
