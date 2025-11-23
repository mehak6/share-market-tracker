#!/usr/bin/env python3
"""Test massive stock symbols loading"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from data.massive_stock_symbols import *

def main():
    print("Testing Massive Stock Symbols...")
    print(f"Total stocks in database: {get_stock_count():,}")
    print()

    # Test search functionality
    print("Sample stocks (empty search):")
    for i, (symbol, name) in enumerate(search_stocks('', 10), 1):
        print(f"{i:2d}. {symbol:15s} - {name}")
    print()

    # Test specific searches
    test_queries = ['REL', 'TCS', 'INFY', 'GENUSPOWER', 'MASTEK', 'GLENMARK']
    for query in test_queries:
        results = search_stocks(query, 3)
        if results:
            print(f"Search '{query}':")
            for symbol, name in results:
                print(f"    {symbol:15s} - {name}")
        else:
            print(f"Search '{query}': No results found")
        print()

if __name__ == "__main__":
    main()