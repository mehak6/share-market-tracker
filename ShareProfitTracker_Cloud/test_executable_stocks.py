#!/usr/bin/env python3
"""Test stock availability in executables"""

import sys
import os
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_stock_access():
    print("TESTING STOCK DATABASE ACCESS")
    print("=" * 50)
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Test 1: Try massive stock symbols
    try:
        from data.massive_stock_symbols import get_stock_count, search_stocks, get_all_indian_stocks
        count = get_stock_count()
        print(f"[SUCCESS] Massive stock database: {count:,} stocks available")

        # Test search for your portfolio stocks
        portfolio_test = ['RELIANCE', 'INFY', 'GLENMARK', 'MASTEK', 'GENUSPOWER', 'MAPMYINDIA', 'PAISALO', 'SYRMA', 'COCHINSHIP', 'VEDL', 'WIPRO']
        found = 0

        print("\nPortfolio Stock Coverage Test:")
        print("-" * 30)
        for stock in portfolio_test:
            results = search_stocks(stock, 1)
            if results:
                symbol, name = results[0]
                print(f"[FOUND] {stock:12s} -> {symbol} - {name[:40]}...")
                found += 1
            else:
                print(f"[MISSING] {stock}")

        print(f"\nCoverage: {found}/{len(portfolio_test)} = {(found/len(portfolio_test)*100):.1f}%")

        if found == len(portfolio_test):
            print("[PERFECT] All portfolio stocks found!")
        elif found >= len(portfolio_test) * 0.8:
            print("[GOOD] Most portfolio stocks found!")
        else:
            print("[LIMITED] Many portfolio stocks missing!")

    except ImportError as e:
        print(f"[ERROR] Cannot import massive stock database: {e}")

    # Test 2: Try old stock symbols
    print("\n" + "=" * 50)
    try:
        from data.stock_symbols import ALL_STOCKS, search_stocks as old_search
        count = len(ALL_STOCKS)
        print(f"[OLD] Original stock database: {count} stocks available")

        # Test old search
        results = old_search('REL', 3)
        if results:
            print("Old database sample results for 'REL':")
            for symbol, name in results:
                print(f"  {symbol:15s} - {name}")

    except ImportError as e:
        print(f"[ERROR] Cannot import old stock database: {e}")

    # Test 3: Check data files
    print("\n" + "=" * 50)
    print("DATA FILE AVAILABILITY:")
    print("-" * 30)

    data_files = [
        'data/massive_stocks_2000plus.json',
        'data/ultra_comprehensive_stocks.json',
        'data/complete_indian_stocks.json',
        'data/mega_stock_database.json'
    ]

    for file_path in data_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) / 1024  # KB
            print(f"[EXISTS] {file_path:35s} ({size:.1f} KB)")
        else:
            print(f"[MISSING] {file_path}")

if __name__ == "__main__":
    test_stock_access()