#!/usr/bin/env python3
"""
Fetch Mega Stock Database - Complete NSE/BSE Coverage (2000+ stocks)

This script fetches the complete database of all NSE and BSE stocks,
providing comprehensive coverage for the entire Indian stock market.
"""

import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from services.mega_stock_fetcher import mega_stock_fetcher

    def main():
        """Fetch and save mega stock database"""
        print("FETCHING MEGA STOCK DATABASE - COMPLETE NSE/BSE COVERAGE")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Step 1: Fetch complete NSE stocks
        print("STEP 1: Fetching Complete NSE Stock Database...")
        print("-" * 50)
        nse_stocks = mega_stock_fetcher.get_complete_nse_stocks()
        print(f"Total NSE stocks fetched: {len(nse_stocks)}")
        print()

        # Step 2: Fetch complete BSE stocks
        print("STEP 2: Fetching Complete BSE Stock Database...")
        print("-" * 50)
        bse_stocks = mega_stock_fetcher.get_complete_bse_stocks()
        print(f"Total BSE stocks fetched: {len(bse_stocks)}")
        print()

        # Step 3: Save mega database
        print("STEP 3: Saving Mega Stock Database...")
        print("-" * 40)
        mega_stock_fetcher.save_mega_database(nse_stocks, bse_stocks)
        print()

        # Step 4: Display statistics
        print("MEGA DATABASE STATISTICS:")
        print("=" * 40)
        print(f"NSE Stocks: {len(nse_stocks):,}")
        print(f"BSE Stocks: {len(bse_stocks):,}")
        print(f"Total Coverage: {len(nse_stocks) + len(bse_stocks):,} stocks")
        print()

        print("SAMPLE NSE STOCKS:")
        print("-" * 30)
        for i, (symbol, name) in enumerate(list(nse_stocks.items())[:10], 1):
            print(f"{i:2d}. {symbol:12s} - {name}")
        if len(nse_stocks) > 10:
            print(f"    ... and {len(nse_stocks) - 10:,} more NSE stocks")
        print()

        print("SAMPLE BSE STOCKS:")
        print("-" * 30)
        for i, (symbol, name) in enumerate(list(bse_stocks.items())[:10], 1):
            print(f"{i:2d}. {symbol:12s} - {name}")
        if len(bse_stocks) > 10:
            print(f"    ... and {len(bse_stocks) - 10:,} more BSE stocks")
        print()

        # Coverage analysis
        total_stocks = len(nse_stocks) + len(bse_stocks)
        if total_stocks >= 2000:
            print("[EXCELLENT] Complete stock market coverage achieved!")
            print("This database now covers virtually ALL traded Indian stocks!")
        elif total_stocks >= 1000:
            print("[VERY GOOD] Comprehensive stock coverage achieved!")
            print("This database covers most major Indian stocks!")
        elif total_stocks >= 500:
            print("[GOOD] Substantial stock coverage achieved!")
        else:
            print("[LIMITED] Using backup database only")

        print()
        print(f"Mega database saved to: data/mega_stock_database.json")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("This mega database provides comprehensive coverage for")
        print("corporate actions notifications across the entire Indian stock market!")

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required packages are installed.")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)