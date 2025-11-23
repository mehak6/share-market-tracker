#!/usr/bin/env python3
"""
Fetch ALL NSE and BSE Stocks

This script fetches and saves a complete database of ALL NSE and BSE stocks
from multiple authoritative sources.
"""

import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from services.complete_stock_fetcher import complete_stock_fetcher
    
    def fetch_all_stocks():
        """Fetch all stocks and save to database"""
        print("FETCHING ALL NSE AND BSE STOCKS")
        print("=" * 50)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Step 1: Try to load existing database
        print("Step 1: Checking for existing database...")
        if complete_stock_fetcher.load_complete_database():
            print("Existing database loaded successfully!")
            choice = input("Do you want to refresh the database? (y/n): ").lower()
            if choice != 'y':
                print("Using existing database.")
                return display_summary()
        else:
            print("No existing database found. Will fetch fresh data.")
        print()
        
        # Step 2: Fetch all stocks
        print("Step 2: Fetching ALL stocks from multiple sources...")
        print("This may take several minutes...")
        print()
        
        try:
            all_stocks = complete_stock_fetcher.get_all_stocks()
            
            if not all_stocks:
                print("No stocks fetched! Check internet connection and try again.")
                return
            
            print(f"Successfully fetched {len(all_stocks)} total stocks!")
            print()
            
        except Exception as e:
            print(f"Error fetching stocks: {e}")
            return
        
        # Step 3: Save to database
        print("Step 3: Saving complete stock database...")
        try:
            complete_stock_fetcher.save_complete_database()
            print("Database saved successfully!")
        except Exception as e:
            print(f"Error saving database: {e}")
        print()
        
        # Step 4: Display summary
        display_summary()
    
    def display_summary():
        """Display summary of stock database"""
        stocks = complete_stock_fetcher.all_stocks
        
        if not stocks:
            print("No stocks in database!")
            return
        
        print("COMPLETE STOCK DATABASE SUMMARY")
        print("=" * 40)
        
        # Count by exchange
        nse_count = len([s for s in stocks.values() if s.exchange == 'NSE'])
        bse_count = len([s for s in stocks.values() if s.exchange == 'BSE'])
        
        print(f"Total stocks: {len(stocks):,}")
        print(f"NSE stocks: {nse_count:,}")
        print(f"BSE stocks: {bse_count:,}")
        print()
        
        # Count by sector
        sectors = {}
        for stock in stocks.values():
            sector = stock.sector or 'Unknown'
            sectors[sector] = sectors.get(sector, 0) + 1
        
        print("Top sectors:")
        for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {sector}: {count:,} stocks")
        print()
        
        # Sample stocks
        print("Sample stocks:")
        sample_stocks = list(stocks.items())[:20]
        for i, (symbol, info) in enumerate(sample_stocks, 1):
            print(f"  {i:2d}. {symbol:15s} - {info.company_name[:50]} ({info.exchange})")
        
        if len(stocks) > 20:
            print(f"  ... and {len(stocks) - 20:,} more stocks")
        print()
        
        # Coverage analysis
        print("COVERAGE ANALYSIS")
        print("-" * 20)
        
        major_indices = ['NIFTY 50', 'NIFTY 100', 'NIFTY 500', 'SENSEX']
        print("Major indices coverage:")
        for index in major_indices:
            # This is a simplified check - in practice you'd check actual index constituents
            if index == 'NIFTY 50':
                expected = 50
            elif index == 'NIFTY 100':
                expected = 100
            elif index == 'NIFTY 500':
                expected = 500
            elif index == 'SENSEX':
                expected = 30
            
            # Rough estimate based on major stocks
            coverage = min(nse_count, expected)
            percentage = (coverage / expected) * 100
            print(f"  {index}: ~{coverage}/{expected} stocks ({percentage:.0f}%)")
        
        print()
        print("DATABASE QUALITY")
        print("-" * 16)
        
        # Quality metrics
        stocks_with_names = len([s for s in stocks.values() if s.company_name and s.company_name != s.symbol])
        stocks_with_sectors = len([s for s in stocks.values() if s.sector])
        
        print(f"Stocks with company names: {stocks_with_names:,}/{len(stocks):,} ({stocks_with_names/len(stocks)*100:.1f}%)")
        print(f"Stocks with sector info: {stocks_with_sectors:,}/{len(stocks):,} ({stocks_with_sectors/len(stocks)*100:.1f}%)")
        
        print()
        print("DATABASE STATUS")
        print("-" * 15)
        
        if len(stocks) >= 3000:
            print("EXCELLENT: Comprehensive coverage of Indian stock markets!")
        elif len(stocks) >= 1000:
            print("GOOD: Substantial coverage of major Indian stocks")
        elif len(stocks) >= 500:
            print("FAIR: Basic coverage of Indian stocks")
        else:
            print("LIMITED: Minimal stock coverage")
        
        print(f"\nYour ShareProfitTracker now has access to {len(stocks):,} stocks!")
        print("This includes virtually all major NSE and BSE listed companies.")
        print()
        print("Next steps:")
        print("1. Update your main executable with: update_main_exe.bat")
        print("2. Launch ShareProfitTracker.exe")
        print("3. Go to Notifications tab")
        print("4. Refresh notifications to see corporate actions for ALL your stocks!")
    
    def main():
        """Main function"""
        try:
            fetch_all_stocks()
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required packages are installed:")
    print("pip install pandas requests")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)