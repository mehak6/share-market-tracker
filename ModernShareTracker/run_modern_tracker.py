#!/usr/bin/env python3
"""
Modern Share Tracker - Main Launcher
Interactive launcher for all modern portfolio features
"""

import asyncio
import sys
import os
from datetime import datetime

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

try:
    from services.ai_chatbot import FinancialAIAdvisor
    from services.price_alerts import RealTimePriceAlertsSystem
    from services.portfolio_rebalancer import PortfolioRebalancingEngine
    from services.tax_optimizer import IndianTaxOptimizer
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required packages:")
    print("pip install numpy pandas requests")
    print("\nFor full functionality (optional):")
    print("pip install openai websocket-client")
    sys.exit(1)


class ModernShareTracker:
    """Main launcher for Modern Share Tracker features"""
    
    def __init__(self):
        self.ai_advisor = FinancialAIAdvisor()
        self.price_alerts = RealTimePriceAlertsSystem()
        self.rebalancer = PortfolioRebalancingEngine()
        self.tax_optimizer = IndianTaxOptimizer()
        
        # Sample portfolio for demo
        self.sample_portfolio = {
            'stocks': [
                {
                    'symbol': 'RELIANCE',
                    'quantity': 100,
                    'purchase_price': 2200,
                    'current_price': 2500,
                    'purchase_date': '2023-06-15T00:00:00',
                    'sector': 'Energy',
                    'current_value': 250000,
                    'invested_amount': 220000,
                    'beta': 1.2,
                    'pe_ratio': 12
                },
                {
                    'symbol': 'TCS',
                    'quantity': 50,
                    'purchase_price': 3500,
                    'current_price': 3200,
                    'purchase_date': '2024-01-10T00:00:00',
                    'sector': 'Technology',
                    'current_value': 160000,
                    'invested_amount': 175000,
                    'beta': 0.8,
                    'pe_ratio': 22
                },
                {
                    'symbol': 'INFY',
                    'quantity': 80,
                    'purchase_price': 1200,
                    'current_price': 1400,
                    'purchase_date': '2022-05-20T00:00:00',
                    'sector': 'Technology',
                    'current_value': 112000,
                    'invested_amount': 96000,
                    'beta': 0.9,
                    'pe_ratio': 18
                },
                {
                    'symbol': 'HDFC',
                    'quantity': 60,
                    'purchase_price': 1400,
                    'current_price': 1600,
                    'purchase_date': '2024-08-01T00:00:00',
                    'sector': 'Banking',
                    'current_value': 96000,
                    'invested_amount': 84000,
                    'beta': 1.1,
                    'pe_ratio': 15
                }
            ]
        }
    
    def show_main_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("🚀 MODERN SHARE TRACKER - Advanced Portfolio Management")
        print("="*60)
        print("1. 🤖 AI Financial Advisor Chat")
        print("2. 🔔 Price Alerts System")
        print("3. ⚖️  Portfolio Rebalancing")
        print("4. 💰 Tax Optimization")
        print("5. 📊 Complete Portfolio Analysis")
        print("6. 🧪 Run All Demos")
        print("0. Exit")
        print("="*60)
    
    async def run_ai_chat(self):
        """Interactive AI chat session"""
        print("\n🤖 AI FINANCIAL ADVISOR")
        print("-" * 40)
        print("Ask me anything about your portfolio!")
        print("Type 'quit' to exit\n")
        
        # Analyze portfolio first
        analysis = await self.ai_advisor.analyze_portfolio(self.sample_portfolio)
        print("Portfolio Analysis Complete! Ask me questions like:")
        print("• How is my portfolio performing?")
        print("• Should I rebalance my portfolio?") 
        print("• What are the tax implications?")
        print("• How can I reduce risk?\n")
        
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input:
                response = await self.ai_advisor.chat_with_advisor(user_input, self.sample_portfolio)
                print(f"\nAI Advisor: {response}\n")
    
    async def run_price_alerts_demo(self):
        """Demo price alerts system"""
        print("\n🔔 PRICE ALERTS SYSTEM DEMO")
        print("-" * 40)
        
        # Create sample alerts
        user_id = "demo_user"
        
        # Price target alerts
        alert1 = await self.price_alerts.create_alert(
            user_id, "RELIANCE", self.price_alerts.AlertType.PRICE_ABOVE, 2600,
            [self.price_alerts.NotificationChannel.POPUP],
            message="RELIANCE hit your target price!"
        )
        
        alert2 = await self.price_alerts.create_alert(
            user_id, "TCS", self.price_alerts.AlertType.PRICE_BELOW, 3000,
            [self.price_alerts.NotificationChannel.POPUP],
            message="TCS support level breached"
        )
        
        print(f"✅ Created price alerts: {alert1}, {alert2}")
        
        # Create smart alerts for portfolio
        smart_alerts = await self.price_alerts.create_smart_alerts(user_id, self.sample_portfolio)
        print(f"✅ Created {len(smart_alerts)} smart alerts for your portfolio")
        
        # Show active alerts
        active_alerts = self.price_alerts.get_active_alerts(user_id)
        print(f"\n📋 Active Alerts: {len(active_alerts)}")
        
        for alert in active_alerts:
            print(f"• {alert.symbol}: {alert.alert_type.value} at ₹{alert.condition_value}")
        
        print("\n🔄 Starting price monitoring... (Press Enter to continue)")
        await self.price_alerts.start_monitoring()
        input()
    
    async def run_rebalancing_demo(self):
        """Demo portfolio rebalancing"""
        print("\n⚖️  PORTFOLIO REBALANCING DEMO")
        print("-" * 40)
        
        # Convert sample portfolio to Stock objects
        from services.portfolio_rebalancer import Stock
        
        stocks = []
        for stock_data in self.sample_portfolio['stocks']:
            stock = Stock(
                symbol=stock_data['symbol'],
                current_price=stock_data['current_price'],
                quantity=stock_data['quantity'],
                purchase_price=stock_data['purchase_price'],
                purchase_date=stock_data['purchase_date'],
                sector=stock_data['sector'],
                market_cap=10000000,  # Mock data
                pe_ratio=stock_data.get('pe_ratio'),
                beta=stock_data.get('beta')
            )
            stocks.append(stock)
        
        # Analyze portfolio
        analysis = await self.rebalancer.analyze_portfolio(stocks)
        print(f"📊 Portfolio Value: ₹{analysis.total_value:,.2f}")
        print(f"📈 Total P&L: ₹{analysis.total_profit_loss:,.2f} ({analysis.total_profit_loss_percent:.1f}%)")
        print(f"⚠️  Risk Score: {analysis.risk_score:.1f}/10")
        
        print("\n🎯 Sector Allocation:")
        for sector, allocation in analysis.sector_allocation.items():
            print(f"   {sector}: {allocation:.1f}%")
        
        # Generate rebalancing suggestions
        strategies = [
            self.rebalancer.RebalancingStrategy.EQUAL_WEIGHT,
            self.rebalancer.RebalancingStrategy.RISK_PARITY
        ]
        
        for strategy in strategies:
            print(f"\n--- {strategy.value.upper()} Strategy ---")
            suggestions = await self.rebalancer.generate_rebalancing_suggestions(
                stocks, strategy, self.rebalancer.RiskTolerance.MODERATE
            )
            
            for suggestion in suggestions[:3]:  # Show top 3
                print(f"• {suggestion.symbol}: {suggestion.action.upper()} "
                      f"(Current: {suggestion.current_allocation:.1%} → "
                      f"Target: {suggestion.target_allocation:.1%})")
                print(f"  Reason: {suggestion.reason}")
    
    async def run_tax_optimization_demo(self):
        """Demo tax optimization"""
        print("\n💰 TAX OPTIMIZATION DEMO")
        print("-" * 40)
        
        # Analyze tax implications
        holdings = []
        for stock in self.sample_portfolio['stocks']:
            holdings.append({
                'symbol': stock['symbol'],
                'quantity': stock['quantity'],
                'purchase_price': stock['purchase_price'],
                'current_price': stock['current_price'],
                'purchase_date': stock['purchase_date'][:10],  # Date only
                'sector': stock['sector']
            })
        
        analysis = await self.tax_optimizer.analyze_portfolio_tax_implications(holdings)
        
        print(f"📊 Unrealized Gains: ₹{analysis['unrealized_analysis']['unrealized_gains']:,.2f}")
        print(f"📊 Unrealized Losses: ₹{analysis['unrealized_analysis']['unrealized_losses']:,.2f}")
        print(f"💸 Tax if sold today: ₹{analysis['unrealized_analysis']['potential_tax_if_sold_today']:,.2f}")
        
        # Generate optimization strategies
        strategies = await self.tax_optimizer.generate_tax_optimization_strategies(
            analysis, available_cash=200000
        )
        
        print(f"\n🎯 Tax Optimization Strategies:")
        for i, strategy in enumerate(strategies[:3], 1):
            print(f"\n{i}. {strategy.strategy_name}")
            print(f"   💰 Potential Saving: ₹{strategy.potential_tax_saving:,.2f}")
            print(f"   ⏰ Timeline: {strategy.timeline}")
            print(f"   📝 {strategy.description}")
        
        # LTCG calendar
        ltcg_calendar = self.tax_optimizer.calculate_holding_period_calendar(holdings)
        print(f"\n📅 Positions becoming LTCG eligible: {ltcg_calendar['total_positions_becoming_ltcg']}")
        print(f"💰 Potential LTCG tax saving: ₹{ltcg_calendar['total_potential_tax_saving']:,.2f}")
    
    async def run_complete_analysis(self):
        """Run complete portfolio analysis"""
        print("\n📊 COMPLETE PORTFOLIO ANALYSIS")
        print("-" * 50)
        
        print("🔄 Running AI analysis...")
        ai_analysis = await self.ai_advisor.analyze_portfolio(self.sample_portfolio)
        
        print("🔄 Analyzing rebalancing opportunities...")
        from services.portfolio_rebalancer import Stock
        stocks = [Stock(s['symbol'], s['current_price'], s['quantity'], 
                       s['purchase_price'], s['purchase_date'], s['sector'])
                 for s in self.sample_portfolio['stocks']]
        rebal_analysis = await self.rebalancer.analyze_portfolio(stocks)
        
        print("🔄 Calculating tax implications...")
        holdings = [{k: v for k, v in s.items() if k in ['symbol', 'quantity', 'purchase_price', 'current_price', 'purchase_date', 'sector']}
                   for s in self.sample_portfolio['stocks']]
        for h in holdings:
            h['purchase_date'] = h['purchase_date'][:10]
        tax_analysis = await self.tax_optimizer.analyze_portfolio_tax_implications(holdings)
        
        # Display summary
        print("\n" + "="*60)
        print("📈 PORTFOLIO SUMMARY")
        print("="*60)
        print(f"Total Portfolio Value: ₹{rebal_analysis.total_value:,.2f}")
        print(f"Total Invested Amount: ₹{rebal_analysis.total_invested:,.2f}")
        print(f"Total Profit/Loss: ₹{rebal_analysis.total_profit_loss:,.2f} ({rebal_analysis.total_profit_loss_percent:.1f}%)")
        print(f"Portfolio Risk Score: {rebal_analysis.risk_score:.1f}/10")
        print(f"Current Tax Liability: ₹{tax_analysis['unrealized_analysis']['potential_tax_if_sold_today']:,.2f}")
        
        print(f"\n🎯 Top Sector: {max(rebal_analysis.sector_allocation.items(), key=lambda x: x[1])[0]}")
        print(f"📊 Number of Holdings: {len(self.sample_portfolio['stocks'])}")
        print(f"⚠️  Concentration Risk: {'High' if rebal_analysis.risk_score > 7 else 'Medium' if rebal_analysis.risk_score > 5 else 'Low'}")
    
    async def run_all_demos(self):
        """Run all system demos"""
        print("\n🧪 RUNNING ALL DEMOS")
        print("="*50)
        
        await self.run_price_alerts_demo()
        input("\nPress Enter to continue to Rebalancing Demo...")
        
        await self.run_rebalancing_demo()
        input("\nPress Enter to continue to Tax Optimization Demo...")
        
        await self.run_tax_optimization_demo()
        input("\nPress Enter to continue to Complete Analysis...")
        
        await self.run_complete_analysis()
        
        print("\n✅ All demos completed!")
    
    async def run(self):
        """Main application loop"""
        print("🚀 Welcome to Modern Share Tracker!")
        print(f"📅 Current Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        while True:
            self.show_main_menu()
            
            try:
                choice = input("\nSelect option (0-6): ").strip()
                
                if choice == '0':
                    print("👋 Thank you for using Modern Share Tracker!")
                    break
                elif choice == '1':
                    await self.run_ai_chat()
                elif choice == '2':
                    await self.run_price_alerts_demo()
                elif choice == '3':
                    await self.run_rebalancing_demo()
                elif choice == '4':
                    await self.run_tax_optimization_demo()
                elif choice == '5':
                    await self.run_complete_analysis()
                elif choice == '6':
                    await self.run_all_demos()
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


async def main():
    """Main entry point"""
    app = ModernShareTracker()
    await app.run()


if __name__ == "__main__":
    print("Starting Modern Share Tracker...")
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")