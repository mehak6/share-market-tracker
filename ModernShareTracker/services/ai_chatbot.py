"""
AI Financial Advisor Chatbot
Advanced AI-powered chatbot for financial advice and portfolio analysis
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
# import openai  # Optional - only needed for real AI integration
from dataclasses import dataclass
import pandas as pd


@dataclass
class ChatMessage:
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None


class FinancialAIAdvisor:
    """Advanced AI Financial Advisor with context awareness"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.conversation_history: List[ChatMessage] = []
        self.user_portfolio_context = {}
        self.market_context = {}
        
        # System prompt for financial expertise
        self.system_prompt = """
        You are an expert financial advisor and portfolio manager with deep knowledge of:
        - Stock market analysis and investment strategies
        - Portfolio optimization and risk management
        - Tax-efficient investing strategies
        - Indian stock market regulations and tax laws
        - Technical and fundamental analysis
        - Asset allocation and diversification principles
        
        Always provide:
        1. Data-driven insights based on the user's portfolio
        2. Risk assessment for any recommendations
        3. Tax implications for Indian investors
        4. Clear actionable advice
        5. Disclaimers when appropriate
        
        Be professional, helpful, and never guarantee returns.
        """
    
    async def analyze_portfolio(self, portfolio_data: Dict) -> Dict[str, Any]:
        """Analyze user's portfolio and generate insights"""
        
        try:
            # Calculate portfolio metrics
            total_value = sum(stock['current_value'] for stock in portfolio_data.get('stocks', []))
            total_invested = sum(stock['invested_amount'] for stock in portfolio_data.get('stocks', []))
            total_profit_loss = total_value - total_invested
            profit_loss_percentage = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
            
            # Sector analysis
            sectors = {}
            for stock in portfolio_data.get('stocks', []):
                sector = stock.get('sector', 'Unknown')
                sectors[sector] = sectors.get(sector, 0) + stock['current_value']
            
            # Risk analysis
            risk_score = await self._calculate_risk_score(portfolio_data)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(portfolio_data, risk_score)
            
            analysis = {
                'portfolio_summary': {
                    'total_value': total_value,
                    'total_invested': total_invested,
                    'profit_loss': total_profit_loss,
                    'profit_loss_percentage': profit_loss_percentage,
                    'number_of_stocks': len(portfolio_data.get('stocks', [])),
                },
                'sector_allocation': sectors,
                'risk_assessment': {
                    'risk_score': risk_score,
                    'risk_level': self._get_risk_level(risk_score),
                    'recommendations': recommendations
                },
                'tax_implications': await self._analyze_tax_implications(portfolio_data),
                'rebalancing_suggestions': await self._generate_rebalancing_suggestions(portfolio_data)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': f'Portfolio analysis failed: {str(e)}'}
    
    async def chat_with_advisor(self, user_message: str, portfolio_data: Optional[Dict] = None) -> str:
        """Main chat interface with AI advisor"""
        
        try:
            # Add user message to history
            self.conversation_history.append(
                ChatMessage(role='user', content=user_message, timestamp=datetime.now())
            )
            
            # Prepare context
            context = await self._prepare_context(portfolio_data)
            
            # Prepare messages for AI
            messages = [
                {"role": "system", "content": self.system_prompt + f"\n\nUser Portfolio Context: {json.dumps(context, indent=2)}"}
            ]
            
            # Add conversation history (last 10 messages)
            for msg in self.conversation_history[-10:]:
                messages.append({"role": msg.role, "content": msg.content})
            
            # Call AI (Mock implementation - replace with actual API)
            response = await self._call_ai_service(messages)
            
            # Add AI response to history
            self.conversation_history.append(
                ChatMessage(role='assistant', content=response, timestamp=datetime.now())
            )
            
            return response
            
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Please try again. Error: {str(e)}"
    
    async def _call_ai_service(self, messages: List[Dict]) -> str:
        """Call AI service (OpenAI GPT or similar)"""
        
        # Mock AI responses for demonstration
        # In production, replace with actual OpenAI API call:
        """
        if self.api_key:
            openai.api_key = self.api_key
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        """
        
        # Mock intelligent responses based on user input
        user_input = messages[-1]["content"].lower()
        
        if "tax" in user_input:
            return """
            Based on your portfolio, here are key tax considerations:
            
            📊 **Short-term vs Long-term Capital Gains:**
            - Stocks held < 1 year: 15% STCG tax
            - Stocks held > 1 year: 10% LTCG tax (on gains > ₹1 lakh)
            
            💡 **Tax Optimization Strategies:**
            1. Consider harvesting losses to offset gains
            2. Plan your selling timeline around the 1-year mark
            3. Use tax-saving instruments (ELSS, PPF) to reduce overall liability
            
            ⚠️ **Disclaimer:** This is general advice. Consult a tax professional for your specific situation.
            """
        
        elif "rebalance" in user_input or "allocation" in user_input:
            return """
            🎯 **Portfolio Rebalancing Analysis:**
            
            **Current Allocation Issues:**
            - Technology sector: 45% (Overweight - Recommended: 25-30%)
            - Banking: 20% (Balanced)
            - Pharmaceuticals: 15% (Underweight - Consider increasing to 20%)
            
            **Recommended Actions:**
            1. **Reduce Tech exposure:** Consider booking profits in overweight tech stocks
            2. **Increase Pharma allocation:** Strong growth prospects
            3. **Add defensive stocks:** FMCG or utilities for stability
            
            **Risk Assessment:** Medium-High due to sector concentration
            
            Would you like specific stock recommendations for rebalancing?
            """
        
        elif "buy" in user_input or "sell" in user_input or "recommend" in user_input:
            return """
            📈 **Investment Recommendations:**
            
            **BUY Suggestions (Based on current market):**
            - **HDFC Bank:** Strong fundamentals, trading near support
            - **Infosys:** Good value after recent correction
            - **Asian Paints:** Defensive play with growth potential
            
            **SELL/REVIEW Suggestions:**
            - Consider booking profits in stocks with >50% gains
            - Review any stock forming >30% of portfolio (concentration risk)
            
            **Market Outlook:** Cautiously optimistic with focus on quality stocks
            
            ⚠️ **Risk Warning:** Past performance doesn't guarantee future returns. Do your own research.
            """
        
        elif "risk" in user_input:
            return """
            🎯 **Portfolio Risk Analysis:**
            
            **Risk Score: 7.5/10 (High)**
            
            **Key Risk Factors:**
            - Sector concentration (Tech heavy)
            - Market cap bias toward large-cap
            - Currency exposure in IT stocks
            
            **Risk Mitigation:**
            1. **Diversify sectors:** Add FMCG, pharma, utilities
            2. **Add mid-cap exposure:** For growth potential
            3. **Consider debt instruments:** For stability (10-20%)
            4. **International diversification:** US/global index funds
            
            **Emergency Fund:** Ensure 6-12 months expenses in liquid funds
            
            Your risk tolerance appears moderate. Consider gradual portfolio adjustments.
            """
        
        else:
            return """
            👋 **How I can help you:**
            
            **Portfolio Analysis:**
            - Risk assessment and optimization
            - Sector allocation review
            - Performance analysis
            
            **Investment Guidance:**
            - Stock recommendations (buy/sell/hold)
            - Market outlook and timing
            - Asset allocation strategies
            
            **Tax Planning:**
            - Capital gains optimization
            - Tax-efficient investing
            - Harvest loss strategies
            
            **Ask me specific questions like:**
            - "Should I rebalance my portfolio?"
            - "What are the tax implications of selling XYZ stock?"
            - "How can I reduce my portfolio risk?"
            - "Which sectors should I invest in now?"
            
            What would you like to know about your investments? 📊
            """
    
    async def _prepare_context(self, portfolio_data: Optional[Dict]) -> Dict:
        """Prepare context for AI analysis"""
        context = {
            'timestamp': datetime.now().isoformat(),
            'market_session': 'open' if self._is_market_open() else 'closed'
        }
        
        if portfolio_data:
            context['portfolio'] = await self.analyze_portfolio(portfolio_data)
        
        return context
    
    async def _calculate_risk_score(self, portfolio_data: Dict) -> float:
        """Calculate portfolio risk score (0-10)"""
        risk_score = 5.0  # Base score
        
        stocks = portfolio_data.get('stocks', [])
        if not stocks:
            return risk_score
        
        # Sector concentration risk
        sectors = {}
        total_value = sum(stock['current_value'] for stock in stocks)
        
        for stock in stocks:
            sector = stock.get('sector', 'Unknown')
            sectors[sector] = sectors.get(sector, 0) + stock['current_value']
        
        # Calculate concentration
        max_sector_weight = max(sectors.values()) / total_value if total_value > 0 else 0
        if max_sector_weight > 0.5:
            risk_score += 2.0  # High concentration risk
        elif max_sector_weight > 0.3:
            risk_score += 1.0  # Medium concentration risk
        
        # Volatility risk (simplified)
        for stock in stocks:
            if stock.get('beta', 1.0) > 1.5:
                risk_score += 0.5  # High volatility
        
        return min(risk_score, 10.0)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to level"""
        if risk_score <= 3:
            return "Low"
        elif risk_score <= 6:
            return "Medium"
        elif risk_score <= 8:
            return "High"
        else:
            return "Very High"
    
    async def _analyze_tax_implications(self, portfolio_data: Dict) -> Dict:
        """Analyze tax implications of current holdings"""
        stocks = portfolio_data.get('stocks', [])
        current_date = datetime.now()
        
        stcg_gains = 0  # Short-term capital gains
        ltcg_gains = 0  # Long-term capital gains
        
        for stock in stocks:
            purchase_date = datetime.fromisoformat(stock.get('purchase_date', current_date.isoformat()))
            days_held = (current_date - purchase_date).days
            
            current_value = stock.get('current_value', 0)
            invested_amount = stock.get('invested_amount', 0)
            gain = current_value - invested_amount
            
            if days_held >= 365:  # Long-term
                ltcg_gains += max(0, gain)
            else:  # Short-term
                stcg_gains += max(0, gain)
        
        # Calculate tax liability
        stcg_tax = stcg_gains * 0.15  # 15% STCG tax
        ltcg_tax = max(0, (ltcg_gains - 100000)) * 0.10  # 10% on gains > 1 lakh
        
        return {
            'stcg_gains': stcg_gains,
            'ltcg_gains': ltcg_gains,
            'stcg_tax': stcg_tax,
            'ltcg_tax': ltcg_tax,
            'total_tax_liability': stcg_tax + ltcg_tax,
            'tax_saving_suggestions': [
                "Consider holding stocks for >1 year for LTCG benefit",
                "Harvest losses to offset gains",
                "Plan selling around financial year-end"
            ]
        }
    
    async def _generate_recommendations(self, portfolio_data: Dict, risk_score: float) -> List[str]:
        """Generate portfolio recommendations"""
        recommendations = []
        
        if risk_score > 7:
            recommendations.append("Consider reducing portfolio concentration")
            recommendations.append("Add defensive stocks or bonds")
        
        stocks = portfolio_data.get('stocks', [])
        if len(stocks) < 10:
            recommendations.append("Consider diversifying with more stocks")
        
        recommendations.append("Review and rebalance quarterly")
        recommendations.append("Maintain emergency fund outside portfolio")
        
        return recommendations
    
    async def _generate_rebalancing_suggestions(self, portfolio_data: Dict) -> List[Dict]:
        """Generate specific rebalancing suggestions"""
        suggestions = []
        
        # Analyze sector allocation
        stocks = portfolio_data.get('stocks', [])
        total_value = sum(stock['current_value'] for stock in stocks)
        
        sectors = {}
        for stock in stocks:
            sector = stock.get('sector', 'Technology')
            sectors[sector] = sectors.get(sector, 0) + stock['current_value']
        
        # Identify overweight sectors
        for sector, value in sectors.items():
            weight = value / total_value if total_value > 0 else 0
            if weight > 0.4:  # Overweight threshold
                suggestions.append({
                    'action': 'reduce',
                    'sector': sector,
                    'current_weight': f"{weight:.1%}",
                    'target_weight': '25-30%',
                    'reason': 'Overweight position increases concentration risk'
                })
        
        return suggestions
    
    def _is_market_open(self) -> bool:
        """Check if market is currently open (simplified)"""
        now = datetime.now()
        # Indian market hours: 9:15 AM to 3:30 PM, Mon-Fri
        if now.weekday() >= 5:  # Weekend
            return False
        
        market_open = now.replace(hour=9, minute=15)
        market_close = now.replace(hour=15, minute=30)
        
        return market_open <= now <= market_close
    
    def get_conversation_summary(self) -> Dict:
        """Get conversation summary and insights"""
        return {
            'total_messages': len(self.conversation_history),
            'last_conversation': self.conversation_history[-1].timestamp if self.conversation_history else None,
            'topics_discussed': self._extract_topics(),
            'advice_given': len([msg for msg in self.conversation_history if msg.role == 'assistant'])
        }
    
    def _extract_topics(self) -> List[str]:
        """Extract topics discussed in conversation"""
        topics = []
        keywords_to_topics = {
            'tax': 'Tax Planning',
            'rebalance': 'Portfolio Rebalancing',
            'risk': 'Risk Assessment',
            'buy': 'Investment Recommendations',
            'sell': 'Investment Recommendations',
            'sector': 'Sector Analysis'
        }
        
        for msg in self.conversation_history:
            if msg.role == 'user':
                for keyword, topic in keywords_to_topics.items():
                    if keyword in msg.content.lower() and topic not in topics:
                        topics.append(topic)
        
        return topics


# Example usage and testing
async def test_ai_advisor():
    """Test the AI Financial Advisor"""
    advisor = FinancialAIAdvisor()
    
    # Sample portfolio data
    sample_portfolio = {
        'stocks': [
            {
                'symbol': 'RELIANCE',
                'sector': 'Energy',
                'current_value': 100000,
                'invested_amount': 80000,
                'purchase_date': '2023-01-15T00:00:00',
                'beta': 1.2
            },
            {
                'symbol': 'TCS',
                'sector': 'Technology',
                'current_value': 150000,
                'invested_amount': 120000,
                'purchase_date': '2023-06-01T00:00:00',
                'beta': 0.8
            }
        ]
    }
    
    # Test portfolio analysis
    analysis = await advisor.analyze_portfolio(sample_portfolio)
    print("Portfolio Analysis:", json.dumps(analysis, indent=2))
    
    # Test chat functionality
    questions = [
        "How is my portfolio performing?",
        "Should I rebalance my portfolio?",
        "What are the tax implications if I sell my TCS shares?",
        "How can I reduce portfolio risk?"
    ]
    
    for question in questions:
        response = await advisor.chat_with_advisor(question, sample_portfolio)
        print(f"\nQ: {question}")
        print(f"A: {response}")
        print("-" * 80)


if __name__ == "__main__":
    asyncio.run(test_ai_advisor())