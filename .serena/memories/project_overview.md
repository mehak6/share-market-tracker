# Share Market Tracking Project - Overview

## Project Type
Desktop Application for Stock Portfolio Management and Profit/Loss Tracking

## Technology Stack
- **Language**: Python 3.9+
- **GUI Framework**: Tkinter (built-in)
- **Database**: SQLite3 (local, serverless)
- **API Integration**: Yahoo Finance (yfinance), NSE Python
- **Packaging**: PyInstaller (creates standalone .exe)
- **Dependencies**: pandas, numpy, openpyxl, aiosqlite, tkcalendar, beautifulsoup4, lxml, requests

## Project Structure
The project consists of TWO main applications:

### 1. ShareProfitTracker (Original/Core)
Located in: `ShareProfitTracker/`
- **Purpose**: Core portfolio tracking application
- **Main Entry**: `main.py`
- **Database**: `portfolio.db`
- **Features**: Portfolio management, cash tracking, tax reports, expense tracking
- **Architecture**: MVC-like pattern with gui/, data/, services/, utils/, controllers/

### 2. ModernShareTracker (Advanced Features)
Located in: `ModernShareTracker/`
- **Purpose**: Enhanced version with AI and advanced features
- **Main Entry**: `unified_share_tracker.py`, `unified_share_tracker_modern.py`
- **Database**: `unified_portfolio.db`
- **Features**: AI advisor, price alerts, portfolio rebalancing, tax optimization
- **Architecture**: Monolithic unified files with services/

## Build Outputs
- `ShareProfitTracker_2000Plus.exe` - Core version with 2000+ stock database
- `ShareProfitTracker_Modern.exe` - Modern version with advanced features
- Build scripts: `build_ultimate_complete.bat`, `build_modern_complete.bat`

## Key Directories
- **ShareProfitTracker/**: Core application source code
- **ModernShareTracker/**: Advanced features version
- **data/**: Contains project documentation and databases
- **.git/**: Git repository
- **.claude/**: Claude Code configuration

## Documentation Files
- `README.md` - Core application documentation
- `share_profit_software_report.md` - Detailed project report
- `Share Profit Tracker - Project Report.pdf` - PDF report
- `MODERN_FEATURES_SUMMARY.md` - Advanced features documentation
