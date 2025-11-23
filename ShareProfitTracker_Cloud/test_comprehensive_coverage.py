#!/usr/bin/env python3
"""
Test Comprehensive NSE/BSE Stock Coverage

This script tests the comprehensive fetcher to verify it can get corporate actions
for all NSE/BSE stocks, not just a limited subset.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from data.async_database import AsyncDatabaseManager
    from data.models import Stock
    from services.comprehensive_nse_bse_fetcher import comprehensive_fetcher
    from utils.config import AppConfig
    
    async def test_comprehensive_coverage():
        """Test the comprehensive NSE/BSE stock coverage"""
        print("TESTING COMPREHENSIVE NSE/BSE STOCK COVERAGE")
        print("=" * 60)
        
        # Initialize database and get portfolio
        db_manager = AsyncDatabaseManager(AppConfig.get_database_path())
        stock_data = await db_manager.get_all_stocks_async()
        stocks = [Stock(**data) for data in stock_data]
        
        print(f"Your portfolio: {len(stocks)} stocks")
        for i, stock in enumerate(stocks, 1):
            print(f"   {i:2d}. {stock.symbol:12s} - {stock.company_name or 'N/A'}")
        print()
        
        # Step 1: Test comprehensive NSE stock fetching
        print("STEP 1: Fetching ALL NSE Stocks...")
        print("-" * 40)
        
        nse_stocks = comprehensive_fetcher.get_all_nse_stocks()
        print(f"Total NSE stocks found: {len(nse_stocks)}")
        
        # Show sample of NSE stocks
        print("Sample NSE stocks:")
        for i, (symbol, name) in enumerate(list(nse_stocks.items())[:10], 1):
            print(f"   {i:2d}. {symbol:12s} - {name}")
        
        if len(nse_stocks) > 10:
            print(f"   ... and {len(nse_stocks) - 10} more stocks")
        print()
        
        # Step 2: Test comprehensive BSE stock fetching
        print("STEP 2: Fetching ALL BSE Stocks...")
        print("-" * 40)
        
        bse_stocks = comprehensive_fetcher.get_all_bse_stocks()
        print(f"Total BSE stocks found: {len(bse_stocks)}")
        
        # Show sample of BSE stocks
        print("Sample BSE stocks:")
        for i, (symbol, name) in enumerate(list(bse_stocks.items())[:10], 1):
            print(f"   {i:2d}. {symbol:12s} - {name}")
        
        if len(bse_stocks) > 10:
            print(f"   ... and {len(bse_stocks) - 10} more stocks")
        print()
        
        # Step 3: Check portfolio coverage
        print("STEP 3: Checking Portfolio Coverage...")
        print("-" * 40)
        
        portfolio_symbols = []
        for stock in stocks:
            portfolio_symbols.append(stock.symbol)
            if not stock.symbol.endswith('.NS'):
                portfolio_symbols.append(f"{stock.symbol}.NS")
        
        covered_stocks = []
        missing_stocks = []
        
        for symbol in portfolio_symbols:
            clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
            
            # Check NSE coverage
            if clean_symbol in nse_stocks:
                covered_stocks.append(f"{symbol} -> NSE: {nse_stocks[clean_symbol]}")
            # Check BSE coverage  
            elif f"{clean_symbol}.BO" in bse_stocks:
                covered_stocks.append(f"{symbol} -> BSE: {bse_stocks[f'{clean_symbol}.BO']}")
            else:
                missing_stocks.append(symbol)
        
        print(f"Portfolio stocks covered: {len(covered_stocks)}/{len(set(portfolio_symbols))}")
        print("Covered stocks:")
        for stock in covered_stocks[:10]:
            print(f"   [Y] {stock}")

        if missing_stocks:
            print(f"\nMissing stocks ({len(missing_stocks)}):")
            for stock in missing_stocks[:10]:
                print(f"   [N] {stock}")
        else:
            print("\n[Y] ALL portfolio stocks are covered in comprehensive database!")
        print()
        
        # Step 4: Test corporate actions fetching
        print("STEP 4: Testing Corporate Actions with Comprehensive Coverage...")
        print("-" * 60)
        
        unique_portfolio_symbols = list(set(portfolio_symbols))
        print(f"Fetching corporate actions for {len(unique_portfolio_symbols)} unique symbols...")
        
        try:
            actions = comprehensive_fetcher.get_comprehensive_corporate_actions(unique_portfolio_symbols)
            
            print(f"\nCORPORATE ACTIONS FOUND: {len(actions)}")
            
            if actions:
                # Group by type
                dividends = [a for a in actions if a.action_type.lower() == 'dividend']
                splits = [a for a in actions if 'split' in a.action_type.lower()]
                bonus = [a for a in actions if 'bonus' in a.action_type.lower()]
                
                print(f"• Dividends: {len(dividends)}")
                print(f"• Splits: {len(splits)}")
                print(f"• Bonus: {len(bonus)}")
                print()
                
                print("SAMPLE CORPORATE ACTIONS:")
                print("-" * 40)
                for i, action in enumerate(actions[:5], 1):
                    print(f"{i}. {action.symbol}")
                    print(f"   Type: {action.action_type.upper()}")
                    print(f"   Ex-Date: {action.ex_date}")
                    if action.dividend_amount:
                        print(f"   Dividend: Rs {action.dividend_amount}")
                    if action.ratio_from and action.ratio_to:
                        print(f"   Ratio: {action.ratio_to}:{action.ratio_from}")
                    print(f"   Source: {action.source or 'NSE/BSE'}")
                    print()
            
        except Exception as e:
            print(f"Error fetching corporate actions: {e}")
        
        # Step 5: Save cache for future use
        print("STEP 5: Saving Comprehensive Stock Cache...")
        print("-" * 40)

        try:
            comprehensive_fetcher.save_cache()
            print("[Y] Comprehensive stock database cached successfully")
        except Exception as e:
            print(f"Error saving cache: {e}")

        print()
        print("SUMMARY:")
        print("=" * 40)
        print(f"NSE stocks in database: {len(nse_stocks):,}")
        print(f"BSE stocks in database: {len(bse_stocks):,}")
        print(f"Total stocks coverage: {len(nse_stocks) + len(bse_stocks):,}")
        print(f"Portfolio coverage: {len(covered_stocks)}/{len(set(portfolio_symbols))}")

        if len(nse_stocks) > 1000:
            print("[Y] EXCELLENT: Comprehensive NSE stock coverage achieved!")
        elif len(nse_stocks) > 500:
            print("[Y] GOOD: Substantial NSE stock coverage")
        else:
            print("[!] LIMITED: Using backup stock list")
        
        print(f"\nThis comprehensive system should now provide corporate actions")
        print(f"for ALL major NSE/BSE stocks, not just a limited subset!")
    
    def main():
        """Main test function"""
        print("Starting Comprehensive Stock Coverage Test...")
        try:
            asyncio.run(test_comprehensive_coverage())
        except Exception as e:
            print(f"Test failed: {e}")
            import traceback
            traceback.print_exc()

    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required packages are installed:")
    print("pip install yfinance requests")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)