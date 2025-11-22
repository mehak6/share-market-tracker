# Architecture and Design Patterns

## ShareProfitTracker Architecture

### Application Structure (MVC-like Pattern)

#### 1. Entry Point
- **File**: `main.py`
- **Purpose**: Application bootstrap, imports gui.main_window, creates MainWindow instance
- **Key Code**: Ensures directories exist, handles import errors, starts event loop

#### 2. GUI Layer (`gui/`)
- **main_window.py**: Primary application window with all UI components
  - Creates tabbed interface (Portfolio, Dashboard, Analytics)
  - Manages toolbar, status bar, user selection
  - Integrates all dialog windows
  - Handles price refresh and export functionality
  
- **add_stock_dialog.py**: Add/Edit stock dialog with autocomplete
- **autocomplete_entry.py**: Custom autocomplete widget for stock symbols
- **cash_management_dialog.py**: Cash deposits/withdrawals management
- **expenses_dialog.py**: Expense tracking by category
- **tax_report_dialog.py**: Comprehensive tax reporting with STCG/LTCG
- **dividend_dialog.py**: Dividend tracking and management
- **stock_adjustment_dialog.py**: Corporate actions (splits, bonus)
- **settings_dialog.py**: Application settings
- **modern_ui.py**: Modern UI styling and components
- **notifications_panel.py**: Real-time notifications display
- **date_picker.py**: Date selection widget

#### 3. Data Layer (`data/`)
- **database.py**: DatabaseManager class
  - SQLite operations with connection pooling
  - All CRUD operations for stocks, users, cash, expenses, dividends
  - Schema initialization
  
- **async_database.py**: AsyncDatabaseManager for non-blocking operations
  
- **models.py**: Data classes
  - Stock dataclass with calculated properties (profit_loss, annualized_return, etc.)
  - PortfolioSummary dataclass
  
- **stock_symbols.py**: Basic stock database (~50 popular stocks)
- **enhanced_stock_symbols.py**: Extended database (~200 stocks)
- **massive_stock_symbols.py**: Comprehensive database (2000+ stocks with JSON fallback)

#### 4. Services Layer (`services/`)
- **price_fetcher.py**: PriceFetcher class
  - Yahoo Finance API integration
  - Rate limiting, caching, batch fetching
  - Fallback to mock data if yfinance unavailable
  
- **unified_price_service.py**: Ultra-fast price fetching with async support
- **calculator.py**: PortfolioCalculator class
  - Portfolio metrics calculation
  - Currency and percentage formatting
  
- **corporate_actions_fetcher.py**: Corporate actions tracking
- **complete_stock_fetcher.py**: Comprehensive stock data fetching
- **ai_chatbot.py**: AI financial advisor (template-based)
- **price_alerts.py**: Real-time price monitoring and alerts
- **portfolio_rebalancer.py**: Portfolio optimization engine
- **tax_optimizer.py**: Indian tax law optimization

#### 5. Controllers Layer (`controllers/`)
- **portfolio_controller.py**: Business logic coordination between GUI and services

#### 6. Utils Layer (`utils/`)
- **config.py**: AppConfig class with application constants
- **helpers.py**: FormatHelper, FileHelper utility classes
- **theme_manager.py**: Dark/Light theme management

### Database Schema

#### Core Tables:
1. **users**: User management with active user tracking
   - id, username, display_name, is_active, created_at

2. **stocks**: Portfolio holdings
   - id, user_id, symbol, company_name, quantity, purchase_price, purchase_date
   - broker, cash_invested, created_at
   - FOREIGN KEY to users

3. **price_cache**: Price caching for performance
   - symbol (PRIMARY KEY), current_price, last_updated

4. **cash_transactions**: Cash flow tracking
   - id, user_id, transaction_type (deposit/withdrawal), amount, description
   - transaction_date, created_at

5. **other_expenses**: Expense tracking
   - id, user_id, category, description, amount, expense_date, created_at

6. **dividends**: Dividend income tracking
   - id, user_id, symbol, company_name, dividend_per_share, total_dividend
   - shares_held, ex_dividend_date, payment_date, record_date
   - dividend_type, tax_deducted, net_dividend, created_at

7. **stock_adjustments**: Corporate actions (splits, bonus, rights)
   - id, symbol, adjustment_type, adjustment_date, ratio_from, ratio_to
   - description, shares_before, shares_after, price_before, price_after

## ModernShareTracker Architecture

### Unified Design
- **Pattern**: Monolithic unified file approach
- **Main Files**: 
  - `unified_share_tracker.py` (with emojis)
  - `unified_share_tracker_modern.py` (professional)
  - `unified_share_tracker_no_emoji.py` (clean)

### Class Structure
- **UnifiedShareTracker**: Main application class
  - Tab-based interface (Notebook widget)
  - Tabs: Portfolio, Analytics, AI Advisor, Price Alerts, Tax Planning, Reports
  - Integrates services directly in the main class

### Advanced Services
All in `services/` directory:
- **ai_chatbot.py**: FinancialAIAdvisor class with portfolio analysis
- **price_alerts.py**: RealTimePriceAlertsSystem with multi-channel notifications
- **portfolio_rebalancer.py**: PortfolioRebalancingEngine with strategies
- **tax_optimizer.py**: IndianTaxOptimizer with tax-saving strategies

## Design Patterns Used

1. **Singleton Pattern**: Database manager, config
2. **Factory Pattern**: Dialog creation in main window
3. **Observer Pattern**: Price updates, notifications
4. **Strategy Pattern**: Portfolio rebalancing strategies
5. **Repository Pattern**: Database access layer
6. **MVC Pattern**: GUI, Controllers, Data separation
7. **Async/Await Pattern**: Non-blocking database and price operations
