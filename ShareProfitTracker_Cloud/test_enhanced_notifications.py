#!/usr/bin/env python3
"""
Test Enhanced Notifications System

This script tests the enhanced notifications system with your actual portfolio data
to verify that you can see corporate actions for all your stocks.
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
    from services.realtime_corporate_actions import realtime_fetcher
    from services.enhanced_corporate_actions import enhanced_corporate_actions_fetcher
    from services.corporate_actions_fetcher import corporate_actions_fetcher
    from utils.config import AppConfig
    
    async def test_notifications():
        """Test the enhanced notifications system"""
        print("Testing Enhanced Notifications System")
        print("=" * 60)
        
        # Initialize database
        db_manager = AsyncDatabaseManager(AppConfig.get_database_path())
        
        # Get actual portfolio stocks
        print("Loading your portfolio...")
        stock_data = await db_manager.get_all_stocks_async()
        stocks = [Stock(**data) for data in stock_data]
        
        if not stocks:
            print("No stocks found in portfolio!")
            print("   Please add some stocks to your portfolio first.")
            return
        
        print(f"Found {len(stocks)} stocks in your portfolio:")
        for i, stock in enumerate(stocks[:10], 1):  # Show first 10
            print(f"   {i:2d}. {stock.symbol:12s} - {stock.company_name or 'N/A'}")
        
        if len(stocks) > 10:
            print(f"   ... and {len(stocks) - 10} more stocks")
        
        print()
        
        # Prepare symbols list
        portfolio_symbols = []
        for stock in stocks:
            portfolio_symbols.append(stock.symbol)
            if not stock.symbol.endswith('.NS'):
                portfolio_symbols.append(f"{stock.symbol}.NS")
        
        print(f"Testing notification fetchers...")
        print(f"   Symbols to check: {len(set(portfolio_symbols))}")
        print()
        
        # Test 1: Real-time comprehensive fetcher
        print("Testing Real-time Comprehensive Fetcher...")
        try:
            rt_actions = realtime_fetcher.get_comprehensive_actions(list(set(portfolio_symbols)))
            print(f"   Real-time fetcher found: {len(rt_actions)} actions")
            
            if rt_actions:
                print("   Sample actions:")
                for action in rt_actions[:3]:
                    print(f"      • {action.symbol} - {action.action_type} on {action.ex_date}")
                    if action.dividend_amount:
                        print(f"        Amount: ₹{action.dividend_amount}")
        except Exception as e:
            print(f"   Real-time fetcher error: {e}")
            rt_actions = []
        print()
        
        # Test 2: Enhanced multi-source fetcher
        print("Testing Enhanced Multi-source Fetcher...")
        try:
            enh_actions = enhanced_corporate_actions_fetcher.get_portfolio_corporate_actions(
                list(set(portfolio_symbols)), days_ahead=90
            )
            print(f"   Enhanced fetcher found: {len(enh_actions)} actions")
            
            if enh_actions:
                print("   Sample actions:")
                for action in enh_actions[:3]:
                    print(f"      • {action.symbol} - {action.action_type} on {action.ex_date}")
                    if action.dividend_amount:
                        print(f"        Amount: ₹{action.dividend_amount}")
        except Exception as e:
            print(f"   Enhanced fetcher error: {e}")
            enh_actions = []
        print()
        
        # Test 3: Original fetcher
        print("Testing Original Fetcher...")
        try:
            orig_actions = corporate_actions_fetcher.get_portfolio_corporate_actions(
                list(set(portfolio_symbols)), days_ahead=60
            )
            print(f"   Original fetcher found: {len(orig_actions)} actions")
            
            if orig_actions:
                print("   Sample actions:")
                for action in orig_actions[:3]:
                    print(f"      • {action.symbol} - {action.action_type} on {action.ex_date}")
                    if action.dividend_amount:
                        print(f"        Amount: ₹{action.dividend_amount}")
        except Exception as e:
            print(f"   Original fetcher error: {e}")
            orig_actions = []
        print()
        
        # Combine all results
        all_actions = []
        all_actions.extend(rt_actions)
        all_actions.extend(enh_actions)
        all_actions.extend(orig_actions)
        
        # Remove duplicates
        unique_actions = []
        seen = set()
        for action in all_actions:
            key = (action.symbol.replace('.NS', '').replace('.BO', ''), 
                   action.action_type, action.ex_date)
            if key not in seen:
                unique_actions.append(action)
                seen.add(key)
        
        print("FINAL RESULTS")
        print("=" * 40)
        print(f"Total unique actions found: {len(unique_actions)}")
        
        if unique_actions:
            # Group by type
            dividends = [a for a in unique_actions if a.action_type.lower() == 'dividend']
            splits = [a for a in unique_actions if 'split' in a.action_type.lower()]
            bonus = [a for a in unique_actions if 'bonus' in a.action_type.lower()]
            
            print(f"• Dividends: {len(dividends)}")
            print(f"• Splits: {len(splits)}")
            print(f"• Bonus: {len(bonus)}")
            print()
            
            print("UPCOMING CORPORATE ACTIONS FOR YOUR PORTFOLIO:")
            print("-" * 60)
            
            for action in sorted(unique_actions, key=lambda x: x.ex_date)[:10]:
                print(f"Symbol: {action.symbol}")
                print(f"   Type: {action.action_type.upper()}")
                print(f"   Ex-Date: {action.ex_date}")
                if action.dividend_amount:
                    print(f"   Amount: ₹{action.dividend_amount}")
                if action.ratio_from and action.ratio_to:
                    print(f"   Ratio: {action.ratio_to}:{action.ratio_from}")
                print(f"   Source: {action.source or 'Unknown'}")
                print()
        
        else:
            print("No corporate actions found for your portfolio stocks.")
            print()
            print("POSSIBLE REASONS:")
            print("   1. Your stocks may not have upcoming corporate actions")
            print("   2. Symbol format issues (.NS suffix missing)")
            print("   3. API limitations or network issues")
            print("   4. Need API keys for better data sources")
            print()
            print("SUGGESTIONS:")
            print("   1. Check if your symbols are correct (e.g., RELIANCE vs RELIANCE.NS)")
            print("   2. Try manually adding .NS suffix to Indian stocks")
            print("   3. Get API keys for Financial Modeling Prep or Alpha Vantage")
            print("   4. The system will show projected dividends based on historical patterns")
        
        print()
        print("Test completed!")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def main():
        """Main test function"""
        print("Starting Enhanced Notifications Test...")
        try:
            asyncio.run(test_notifications())
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