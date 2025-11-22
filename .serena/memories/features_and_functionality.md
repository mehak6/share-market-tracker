# Features and Functionality

## Core Features (ShareProfitTracker)

### 1. Portfolio Management
- **Add/Edit/Delete Stocks**
  - Symbol autocomplete with 2000+ Indian stocks
  - Quantity, purchase price, purchase date tracking
  - Broker information (optional)
  - Actual cash invested vs calculated investment tracking
  
- **Multi-User Support**
  - User creation and switching via dropdown
  - User-specific portfolios
  - Active user tracking
  
- **Stock Details**
  - Current price (auto-fetched from Yahoo Finance)
  - Profit/Loss amount and percentage
  - Current value calculation
  - Days held tracking
  - Annualized return calculation

### 2. Real-Time Price Updates
- **Price Fetching**
  - Yahoo Finance API integration via yfinance library
  - Ultra-fast batch fetching for multiple stocks
  - Async/await support for non-blocking operations
  - Price caching to reduce API calls
  - Mock mode fallback if yfinance unavailable
  
- **Refresh Mechanisms**
  - Manual refresh button
  - Auto-refresh option (configurable interval)
  - Last update timestamp display
  - Rate limiting to prevent API throttling

### 3. Financial Analytics
- **Portfolio Summary**
  - Total investment
  - Current portfolio value
  - Overall profit/loss (amount and percentage)
  - Number of stocks
  - Best/worst performing stocks
  
- **Individual Stock Metrics**
  - Purchase price vs current price
  - Profit/loss per stock
  - Percentage gain/loss
  - Days held
  - Annualized return
  - Current value

### 4. Cash Management
- **Cash Tracking**
  - Deposit transactions (money added)
  - Withdrawal transactions (money taken out)
  - Current cash balance calculation
  - Transaction history with descriptions
  - Transaction date tracking
  
- **Cash vs Investment Reconciliation**
  - Actual cash invested tracking per stock
  - Total cash deployed in portfolio
  - Available cash display

### 5. Expense Tracking
- **Categories**
  - Electricity, Rent, Food, Transportation, Healthcare
  - Entertainment, Education, Shopping, Other
  
- **Expense Management**
  - Add/edit/delete expenses
  - Amount and description
  - Date tracking
  - Category-wise breakdown
  - Monthly expense summaries
  - Total expenses calculation
  - Remaining cash after expenses

### 6. Tax Reporting
- **Capital Gains Classification**
  - Short-Term Capital Gains (STCG): Held < 1 year
  - Long-Term Capital Gains (LTCG): Held ≥ 1 year
  
- **Indian Tax Rates (Built-in)**
  - STCG: 15.6% (15% + surcharge/cess)
  - LTCG: 10.4% (10% + surcharge/cess)
  
- **Tax Report Features**
  - Current holdings with gain/loss classification
  - Potential tax liability if sold today
  - Realized gains tracking (sold stocks)
  - Unrealized gains for tax planning
  - Export to CSV for accountants
  - Year-wise tax summaries

### 7. Dividend Tracking
- **Dividend Recording**
  - Symbol and company name
  - Dividend per share
  - Total dividend received
  - Number of shares held
  - Ex-dividend date, payment date, record date
  - Dividend type (regular, special, bonus)
  - Tax deducted at source (TDS)
  - Net dividend received
  
- **Dividend Analytics**
  - Total dividend income
  - Dividend yield calculations
  - Dividend history per stock

### 8. Corporate Actions
- **Action Types**
  - Stock splits (e.g., 1:2, 1:5)
  - Bonus issues (e.g., 1:1, 1:2)
  - Rights issues
  
- **Adjustment Tracking**
  - Adjustment date
  - Ratio (from:to)
  - Shares before/after
  - Price before/after
  - Description and notes

### 9. Data Export
- **Export Formats**
  - CSV (Comma-separated values)
  - Excel (via openpyxl)
  
- **Export Types**
  - Portfolio summary
  - Stock holdings
  - Cash transactions
  - Expense reports
  - Tax reports
  - Dividend history

### 10. UI/UX Features
- **Themes**
  - Dark mode
  - Light mode
  - Theme persistence (saves preference)
  
- **Search and Filter**
  - Search stocks by symbol or company name
  - Sort by multiple columns (profit/loss, value, days held)
  - Ascending/descending sort order
  
- **Modern UI**
  - Professional color schemes
  - Responsive layout
  - Metric cards for key stats
  - Tabbed interface
  - Status bar with balance
  - Toolbar with quick actions
  
- **Notifications Panel**
  - Real-time portfolio updates
  - Price change notifications
  - Corporate action alerts
  - Dividend announcements

## Advanced Features (ModernShareTracker)

### 1. AI Financial Advisor
- **Capabilities**
  - Portfolio analysis and insights
  - Investment recommendations
  - Risk assessment
  - Sector allocation analysis
  - Tax implications advice
  - Rebalancing suggestions
  
- **Chat Interface**
  - Natural language queries
  - Context-aware responses
  - Conversation history
  - Portfolio-specific advice
  
- **Analysis Types**
  - Performance analysis
  - Risk-return profile
  - Diversification analysis
  - Tax optimization suggestions

### 2. Real-Time Price Alerts
- **Alert Types**
  - Price threshold alerts (above/below target)
  - Percentage change alerts (daily gain/loss %)
  - Stop-loss alerts
  - Profit target alerts
  
- **Notification Channels**
  - Email notifications
  - Desktop notifications
  - SMS alerts (configurable)
  - In-app notifications
  
- **Smart Features**
  - Auto-disable after trigger
  - Alert history tracking
  - Multiple alerts per stock
  - Condition-based triggers

### 3. Portfolio Rebalancing
- **Rebalancing Strategies**
  - Equal weight (equal allocation to all stocks)
  - Risk parity (allocation based on risk)
  - Market cap weighted
  - Sector-based rebalancing
  
- **Rebalancing Features**
  - Current vs target allocation comparison
  - Buy/sell recommendations to rebalance
  - Tax-efficient rebalancing (considering holding period)
  - Risk metrics calculation
  
- **Reports**
  - Rebalancing suggestions
  - Expected transactions
  - Tax impact analysis
  - Cost-benefit analysis

### 4. Tax Optimization
- **Indian Tax Strategies**
  - Tax loss harvesting opportunities
  - LTCG exemption (₹1 lakh) optimization
  - Holding period optimization calendar
  - Year-end tax planning checklist
  
- **Tax Planning Features**
  - Identify loss-making positions for harvesting
  - Calculate optimal sale timing
  - Tax liability projections
  - Exemption utilization tracking
  
- **Reports**
  - Tax-saving recommendations
  - Projected tax liability
  - Wash sale warnings
  - Holding period calendar

## Data Validation and Error Handling

### Input Validation
- Stock symbol validation
- Positive quantity/price validation
- Date format validation
- Duplicate entry prevention

### Error Handling
- Network failure graceful handling
- API rate limit management
- Database error recovery
- Missing data handling
- Mock data fallback mode

### Data Integrity
- Foreign key constraints
- Transaction atomicity
- Backup recommendations
- Data export for safety
