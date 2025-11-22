#!/usr/bin/env python3
"""
Modern Share Tracker - Simple Launcher (No External Dependencies)
Works with built-in Python libraries only
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any

print("🚀 Modern Share Tracker - Simple Mode")
print("="*50)


def show_sample_portfolio_analysis():
    """Show sample portfolio analysis without external libraries"""
    
    # Sample portfolio data
    portfolio = {
        'RELIANCE': {'qty': 100, 'buy': 2200, 'current': 2500, 'sector': 'Energy'},
        'TCS': {'qty': 50, 'buy': 3500, 'current': 3200, 'sector': 'Technology'},
        'INFY': {'qty': 80, 'buy': 1200, 'current': 1400, 'sector': 'Technology'},
        'HDFC': {'qty': 60, 'buy': 1400, 'current': 1600, 'sector': 'Banking'}
    }
    
    print("\n📊 PORTFOLIO ANALYSIS")
    print("-" * 40)
    
    total_invested = 0
    total_current = 0
    
    print(f"{'Stock':<8} {'Qty':<4} {'Buy':<6} {'Current':<8} {'P&L':<10} {'%':<6}")
    print("-" * 50)
    
    for symbol, data in portfolio.items():
        invested = data['qty'] * data['buy']
        current_val = data['qty'] * data['current']
        pnl = current_val - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0
        
        total_invested += invested
        total_current += current_val
        
        print(f"{symbol:<8} {data['qty']:<4} {data['buy']:<6} {data['current']:<8} "
              f"{pnl:>8,.0f} {pnl_pct:>5.1f}%")
    
    total_pnl = total_current - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    print("-" * 50)
    print(f"{'TOTAL':<8} {'':<4} {'':<6} {'':<8} {total_pnl:>8,.0f} {total_pnl_pct:>5.1f}%")
    print(f"\nTotal Invested: ₹{total_invested:,}")
    print(f"Current Value:  ₹{total_current:,}")
    print(f"Total P&L:      ₹{total_pnl:,} ({total_pnl_pct:.1f}%)")
    
    return portfolio


def show_ai_responses():
    """Show sample AI advisor responses"""
    
    print("\n🤖 AI FINANCIAL ADVISOR DEMO")
    print("-" * 40)
    
    qa_pairs = [
        {
            "q": "How is my portfolio performing?",
            "a": """📈 Your portfolio is performing well with 8.2% overall gains!

Key Highlights:
• Total Value: ₹6,18,000 (up from ₹5,70,000 invested)
• Best Performer: INFY +16.7% (₹16,000 gain)
• Underperformer: TCS -8.6% (₹15,000 loss)
• Technology sector: 44% of portfolio (potentially overweight)

💡 Consider: Rebalancing tech exposure and booking profits in INFY."""
        },
        {
            "q": "Should I rebalance my portfolio?",
            "a": """⚖️ Yes, rebalancing recommended:

🔴 Issues Identified:
• Technology: 44% (Overweight - Target: 25-30%)
• Energy: 40% (High concentration risk)
• Banking: Only 16% (Underweight for stability)

✅ Suggested Actions:
1. Book partial profits in RELIANCE (40% → 25%)
2. Reduce INFY position (sell 30 shares)
3. Add banking/FMCG stocks for diversification
4. Consider HDFC Bank, ITC for balance"""
        },
        {
            "q": "What are the tax implications?",
            "a": """💰 Tax Analysis (Indian Tax Laws):

STCG (Short-term < 1 year): 15.6% tax
• TCS: ₹15,000 loss (can offset gains)
• HDFC: ₹12,000 gain → ₹1,872 tax

LTCG (Long-term > 1 year): 10.4% on gains > ₹1 lakh
• RELIANCE: ₹30,000 gain → ₹0 tax (within exemption)
• INFY: ₹16,000 gain → ₹0 tax (within exemption)

🎯 Tax Optimization:
• Total tax liability if sold today: ₹1,872
• Consider holding TCS for loss harvesting
• LTCG exemption still available: ₹54,000"""
        }
    ]
    
    for qa in qa_pairs:
        print(f"\n❓ {qa['q']}")
        print(f"🤖 {qa['a']}")
        print("-" * 60)


def show_price_alerts_demo():
    """Show price alerts functionality"""
    
    print("\n🔔 PRICE ALERTS SYSTEM")
    print("-" * 40)
    
    alerts = [
        "✅ RELIANCE: Alert if price > ₹2,600 (Target reached)",
        "⚠️  TCS: Alert if price < ₹3,000 (Stop-loss level)",
        "📈 INFY: Alert on 5% daily gain (Momentum signal)",
        "🛡️  HDFC: Alert if price < ₹1,520 (5% stop-loss)"
    ]
    
    print("Smart Alerts Created:")
    for alert in alerts:
        print(f"  {alert}")
    
    print(f"\n📱 Notification Channels:")
    print("  • Desktop Popup ✅")
    print("  • Email (configure SMTP) 📧")
    print("  • SMS (configure Twilio) 📱")
    print("  • Sound Alert 🔊")
    
    print(f"\n🔄 Monitoring Status: Active")
    print(f"📊 Price Update Frequency: Every 10 seconds")


def show_rebalancing_suggestions():
    """Show portfolio rebalancing suggestions"""
    
    print("\n⚖️ PORTFOLIO REBALANCING SUGGESTIONS")
    print("-" * 50)
    
    strategies = [
        {
            "name": "Equal Weight Strategy",
            "suggestions": [
                "RELIANCE: SELL 25 shares (40% → 25%)",
                "TCS: HOLD (current allocation acceptable)",
                "INFY: SELL 20 shares (29% → 20%)", 
                "HDFC: BUY 15 shares (16% → 25%)"
            ]
        },
        {
            "name": "Risk Parity Strategy",
            "suggestions": [
                "RELIANCE: REDUCE (High beta = 1.2)",
                "TCS: INCREASE (Low beta = 0.8)",
                "INFY: HOLD (Beta = 0.9)",
                "HDFC: INCREASE (Stable banking sector)"
            ]
        }
    ]
    
    for strategy in strategies:
        print(f"\n🎯 {strategy['name']}:")
        for suggestion in strategy['suggestions']:
            print(f"   • {suggestion}")
    
    print(f"\n💡 Risk Assessment:")
    print(f"   Current Risk Score: 7.5/10 (High)")
    print(f"   After Rebalancing: 5.2/10 (Medium)")
    print(f"   Main Risk: Sector concentration in Tech + Energy")


def show_tax_optimization():
    """Show tax optimization strategies"""
    
    print("\n💰 TAX OPTIMIZATION STRATEGIES")
    print("-" * 50)
    
    strategies = [
        {
            "name": "Tax Loss Harvesting",
            "saving": "₹2,340",
            "description": "Sell TCS loss (₹15,000) to offset HDFC gain (₹12,000)",
            "timeline": "Before March 31st"
        },
        {
            "name": "LTCG Exemption Optimization", 
            "saving": "₹4,784",
            "description": "Book ₹46,000 LTCG gains within ₹1 lakh exemption limit",
            "timeline": "Current financial year"
        },
        {
            "name": "Hold for LTCG Status",
            "saving": "₹1,248",
            "description": "Hold HDFC for 127 more days to get LTCG treatment",
            "timeline": "Next 4 months"
        },
        {
            "name": "Tax-Saving Investments",
            "saving": "₹46,800",
            "description": "Invest ₹1.5L in ELSS, ₹50K in NPS for Section 80C/80CCD1B",
            "timeline": "Current FY"
        }
    ]
    
    total_saving = sum(float(s['saving'].replace('₹', '').replace(',', '')) for s in strategies)
    
    for i, strategy in enumerate(strategies, 1):
        print(f"{i}. {strategy['name']}")
        print(f"   💰 Potential Saving: {strategy['saving']}")
        print(f"   📝 {strategy['description']}")
        print(f"   ⏰ Timeline: {strategy['timeline']}\n")
    
    print(f"🎯 Total Optimization Potential: ₹{total_saving:,.0f}")
    print(f"📊 Current Tax Liability: ₹1,872")
    print(f"📉 After Optimization: ₹0 (Plus ₹46,800 income tax savings)")


def show_year_end_checklist():
    """Show year-end tax planning checklist"""
    
    print("\n📋 YEAR-END TAX CHECKLIST")
    print("-" * 40)
    
    checklist = {
        "📈 Capital Gains Review": [
            "Calculate total gains and losses for FY 2024-25",
            "Book losses to offset gains (tax harvesting)",
            "Use LTCG exemption limit (₹1 lakh)",
            "Plan timing of profit booking"
        ],
        "💳 Tax-Saving Investments": [
            "Complete Section 80C investments (₹1.5L limit)",
            "Additional NPS contribution (₹50K under 80CCD1B)",
            "Health insurance premium payments (80D)",
            "Review all eligible deductions"
        ],
        "📄 Documentation": [
            "Collect transaction statements",
            "Calculate exact capital gains with dates",
            "Organize dividend income records",
            "Prepare for tax filing"
        ]
    }
    
    for category, items in checklist.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  ✓ {item}")


def main_menu():
    """Interactive main menu"""
    
    while True:
        print("\n" + "="*60)
        print("🚀 MODERN SHARE TRACKER - Simple Demo Mode")
        print("="*60)
        print("1. 📊 Portfolio Analysis")
        print("2. 🤖 AI Advisor Demo")
        print("3. 🔔 Price Alerts Demo")
        print("4. ⚖️  Rebalancing Suggestions")
        print("5. 💰 Tax Optimization")
        print("6. 📋 Year-End Tax Checklist")
        print("7. 🎮 Run All Demos")
        print("8. 📖 System Information")
        print("0. Exit")
        print("="*60)
        
        try:
            choice = input("Select option (0-8): ").strip()
            
            if choice == '0':
                print("👋 Thank you for trying Modern Share Tracker!")
                break
            elif choice == '1':
                portfolio = show_sample_portfolio_analysis()
            elif choice == '2':
                show_ai_responses()
            elif choice == '3':
                show_price_alerts_demo()
            elif choice == '4':
                show_rebalancing_suggestions()
            elif choice == '5':
                show_tax_optimization()
            elif choice == '6':
                show_year_end_checklist()
            elif choice == '7':
                print("🎮 RUNNING ALL DEMOS...")
                show_sample_portfolio_analysis()
                input("Press Enter to continue...")
                show_ai_responses()
                input("Press Enter to continue...")
                show_price_alerts_demo()
                input("Press Enter to continue...")
                show_rebalancing_suggestions()
                input("Press Enter to continue...")
                show_tax_optimization()
                input("Press Enter to continue...")
                show_year_end_checklist()
                print("✅ All demos completed!")
            elif choice == '8':
                print("\n📖 SYSTEM INFORMATION")
                print("-" * 40)
                print("🚀 Modern Share Tracker v1.0")
                print("📅 Built: December 2024")
                print("🐍 Python: Built-in libraries only (this demo)")
                print("📁 Location: F:/share mkt/ModernShareTracker/")
                print("\n💡 Features:")
                print("  ✅ AI Financial Advisor")
                print("  ✅ Real-time Price Alerts")
                print("  ✅ Portfolio Rebalancing")
                print("  ✅ Tax Optimization (Indian Laws)")
                print("\n🔧 For Full Version:")
                print("  pip install numpy pandas requests")
                print("  python run_modern_tracker.py")
                print("\n📚 Files Created:")
                print("  • services/ai_chatbot.py")
                print("  • services/price_alerts.py")
                print("  • services/portfolio_rebalancer.py")
                print("  • services/tax_optimizer.py")
            else:
                print("❌ Invalid option. Please try again.")
            
            if choice != '0':
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("Press Enter to continue...")


if __name__ == "__main__":
    print("🎯 This is a simplified demo version that works without any external packages.")
    print("📦 For full functionality, install packages and run: python run_modern_tracker.py")
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        main_menu()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")