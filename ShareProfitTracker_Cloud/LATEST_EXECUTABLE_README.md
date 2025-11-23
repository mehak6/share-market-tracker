# ShareProfitTracker Latest Executable

## 📦 Latest Release: ShareProfitTracker_v2025_09_13.exe

### ✨ What's New in This Version

This executable includes all the latest enhancements made to the ShareProfitTracker application:

#### 🔔 Enhanced Notifications System
- **Portfolio-Specific Information**: Shows personalized data for each corporate action affecting your stocks
- **Dividend Calculations**: Displays your holding quantity and expected dividend income
- **Stock Split Impact**: Shows additional shares you'll receive from stock splits
- **Bonus Share Analysis**: Calculates bonus shares based on your current holdings
- **Smart Stock Matching**: Improved symbol matching logic to handle .NS suffixes

#### 🔄 Improved Refresh Features
- **Visual Status Indicators**: Enhanced refresh button with emoji indicators and status feedback
- **Auto-Refresh Option**: New 30-second auto-refresh functionality for notifications
- **Better Error Handling**: Clear error messages and status updates

#### 📊 Summary Dashboard
- **Portfolio Impact Analysis**: Shows total actions affecting your portfolio vs. total actions found
- **Breakdown by Type**: Clear categorization of dividends, splits, and bonus shares
- **Total Expected Income**: Automatic calculation of total expected dividend income

### 🎯 Key Features

#### Notifications Panel Enhancements
- **Real-time Updates**: Notifications automatically refresh when portfolio changes
- **Personalized Calculations**: Shows exactly how much dividend income you'll receive
- **Stock Impact Analysis**: See how splits and bonus shares will affect your holdings
- **Visual Status Indicators**: Clear feedback on refresh status and errors
- **Auto-refresh Option**: Keep notifications current without manual intervention

#### Example Notification Display
```
🔔 CORPORATE ACTIONS FOUND (3)

📊 SUMMARY
──────────────────────────────────────────────────
• Actions affecting your portfolio: 2/3
• Dividends: 2 | Splits: 1 | Bonus: 0
• Total expected dividend income: ₹1,250.00

💰 DIVIDENDS
──────────────────────────────────────────────────
• RELIANCE.NS - Ex-Date: 2025-09-20
  Company: Reliance Industries | Amount: ₹8.50 | Your Holdings: 100 shares | Expected Dividend: ₹850.00

• TCS.NS - Ex-Date: 2025-09-25
  Company: Tata Consultancy Services | Amount: ₹20.00 | Your Holdings: 20 shares | Expected Dividend: ₹400.00
```

### 📋 File Information

- **File Name**: `ShareProfitTracker_v2025_09_13.exe`
- **File Size**: 37 MB
- **Build Date**: September 13, 2025
- **Compatible with**: Windows 10/11 (64-bit)

### 🚀 How to Run

1. **Download**: The executable is located in the `dist/` folder
2. **Run**: Double-click `ShareProfitTracker_v2025_09_13.exe` to launch
3. **No Installation Required**: This is a standalone executable
4. **Data Persistence**: Your portfolio data will be saved automatically

### 📁 Files Included

The executable automatically includes:
- All GUI components with latest enhancements
- Enhanced notifications panel
- Database management (SQLite)
- Price fetching services
- Corporate actions fetcher
- Modern UI themes
- Configuration files

### 🛠️ Technical Details

#### Build Configuration
- **PyInstaller Version**: 6.15.0
- **Python Version**: 3.13.7
- **Build Type**: Single file executable (--onefile)
- **Console**: Disabled (windowed application)
- **UPX Compression**: Enabled for smaller file size

#### Dependencies Included
- tkinter (GUI framework)
- yfinance (stock data)
- requests (HTTP requests)
- pandas/numpy (data processing)
- sqlite3 (database)
- urllib3/certifi (secure connections)

### 🔧 Requirements

- **Operating System**: Windows 10 or later (64-bit)
- **RAM**: Minimum 4GB recommended
- **Storage**: ~50MB free space
- **Internet**: Required for fetching stock prices and corporate actions

### 🆕 What's Different from Previous Versions

#### Previous Version Issues Fixed
- ✅ Better module loading and import handling
- ✅ Improved data file inclusion
- ✅ Enhanced error messages
- ✅ More stable GUI components

#### New Features Added
- ✅ Portfolio-specific notification calculations
- ✅ Auto-refresh for notifications
- ✅ Enhanced visual status indicators
- ✅ Summary dashboard for corporate actions
- ✅ Better stock symbol matching

### 🐛 Known Issues

- Some antivirus software may flag the executable as suspicious (false positive)
- First launch may take a few seconds to initialize
- Corporate actions data depends on external APIs

### 🤝 Support

If you encounter any issues:
1. Check your internet connection
2. Ensure Windows Defender/antivirus allows the application
3. Try running as administrator if needed
4. Check the console output for error messages

### 📝 Version History

- **v2025_09_13**: Latest with enhanced notifications and auto-refresh
- **v2025_09_12**: Performance improvements
- **v2025_09_11**: Initial executable builds

---

**Build completed successfully on September 13, 2025**
**Ready to use with all latest enhancements!** 🎉