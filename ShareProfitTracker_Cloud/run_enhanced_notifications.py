#!/usr/bin/env python3
"""
Enhanced Notifications Runner - Quick Fix

Run this to see notifications for your portfolio stocks immediately.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set encoding to UTF-8 to avoid Unicode issues
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

try:
    from data.async_database import AsyncDatabaseManager
    from data.models import Stock
    from services.realtime_corporate_actions import realtime_fetcher
    from services.enhanced_corporate_actions import enhanced_corporate_actions_fetcher
    from services.corporate_actions_fetcher import corporate_actions_fetcher
    from utils.config import AppConfig
    
    async def get_notifications():
        """Get notifications for your portfolio"""
        print("ENHANCED PORTFOLIO NOTIFICATIONS")
        print("=" * 50)
        
        # Get portfolio stocks
        db_manager = AsyncDatabaseManager(AppConfig.get_database_path())
        stock_data = await db_manager.get_all_stocks_async()
        stocks = [Stock(**data) for data in stock_data]
        
        print(f"Portfolio stocks: {len(stocks)}")
        
        # Prepare symbols
        portfolio_symbols = []
        for stock in stocks:
            portfolio_symbols.append(stock.symbol)
            if not stock.symbol.endswith('.NS'):
                portfolio_symbols.append(f"{stock.symbol}.NS")
        
        unique_symbols = list(set(portfolio_symbols))
        print(f"Checking symbols: {unique_symbols[:5]}...")
        print()
        
        # Try multiple fetchers and combine results
        all_actions = []
        
        # Method 1: Original fetcher (most reliable for Indian stocks)
        try:
            orig_actions = corporate_actions_fetcher.get_portfolio_corporate_actions(
                unique_symbols, days_ahead=90
            )
            all_actions.extend(orig_actions)
            print(f"Original fetcher: {len(orig_actions)} actions")
        except Exception as e:
            print(f"Original fetcher error: {e}")
        
        # Method 2: Enhanced fetcher
        try:
            enh_actions = enhanced_corporate_actions_fetcher.get_portfolio_corporate_actions(
                unique_symbols, days_ahead=90
            )
            all_actions.extend(enh_actions)
            print(f"Enhanced fetcher: {len(enh_actions)} actions")
        except Exception as e:
            print(f"Enhanced fetcher error: {e}")
        
        # Remove duplicates
        unique_actions = []
        seen = set()
        for action in all_actions:
            key = (action.symbol.replace('.NS', '').replace('.BO', ''), 
                   action.action_type, action.ex_date)
            if key not in seen:
                unique_actions.append(action)
                seen.add(key)
        
        print(f"Total unique actions: {len(unique_actions)}")
        print()
        
        if unique_actions:
            # Group by type
            dividends = [a for a in unique_actions if a.action_type.lower() == 'dividend']
            splits = [a for a in unique_actions if 'split' in a.action_type.lower()]
            bonus = [a for a in unique_actions if 'bonus' in a.action_type.lower()]
            
            print("CORPORATE ACTIONS SUMMARY:")
            print(f"- Dividends: {len(dividends)}")
            print(f"- Splits: {len(splits)}")
            print(f"- Bonus: {len(bonus)}")
            print()
            
            print("UPCOMING CORPORATE ACTIONS:")
            print("-" * 40)
            
            for i, action in enumerate(sorted(unique_actions, key=lambda x: x.ex_date), 1):
                print(f"{i}. {action.symbol}")
                print(f"   Type: {action.action_type.upper()}")
                print(f"   Ex-Date: {action.ex_date}")
                
                if action.dividend_amount:
                    print(f"   Dividend: Rs {action.dividend_amount}")
                    
                    # Calculate your expected dividend
                    for stock in stocks:
                        if (stock.symbol == action.symbol or 
                            stock.symbol == action.symbol.replace('.NS', '') or
                            f"{stock.symbol}.NS" == action.symbol):
                            expected = action.dividend_amount * stock.quantity
                            print(f"   Your holdings: {stock.quantity:.0f} shares")
                            print(f"   Expected dividend: Rs {expected:.2f}")
                            break
                
                if action.ratio_from and action.ratio_to:
                    print(f"   Ratio: {action.ratio_to}:{action.ratio_from}")
                    
                    # Calculate additional shares
                    for stock in stocks:
                        if (stock.symbol == action.symbol or 
                            stock.symbol == action.symbol.replace('.NS', '') or
                            f"{stock.symbol}.NS" == action.symbol):
                            additional = stock.quantity * (action.ratio_to / action.ratio_from) - stock.quantity
                            print(f"   Your holdings: {stock.quantity:.0f} shares")
                            print(f"   Additional shares: {additional:.0f}")
                            break
                
                if hasattr(action, 'purpose') and action.purpose:
                    print(f"   Purpose: {action.purpose}")
                
                print(f"   Source: {getattr(action, 'source', 'Database')}")
                print()
        
        else:
            print("No upcoming corporate actions found.")
            print()
            print("This could mean:")
            print("1. No dividends/splits/bonus scheduled for your stocks")
            print("2. Actions are beyond 90-day horizon")
            print("3. Need better data sources")
            print()
            print("Your portfolio stocks:")
            for stock in stocks:
                print(f"  - {stock.symbol} ({stock.company_name})")
    
    def main():
        """Run the notifications"""
        try:
            asyncio.run(get_notifications())
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required packages are installed:")
    print("pip install yfinance requests")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()