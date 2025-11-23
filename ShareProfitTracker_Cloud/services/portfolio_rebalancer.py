"""
Portfolio Rebalancing Suggestions Engine
Advanced portfolio optimization and rebalancing recommendations
"""

import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import math
import asyncio


class RebalancingStrategy(Enum):
    EQUAL_WEIGHT = "equal_weight"
    MARKET_CAP_WEIGHT = "market_cap_weight"
    RISK_PARITY = "risk_parity"
    MOMENTUM = "momentum"
    VALUE = "value"
    QUALITY = "quality"
    CUSTOM = "custom"


class RiskTolerance(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class Stock:
    symbol: str
    current_price: float
    quantity: int
    purchase_price: float
    purchase_date: str
    sector: str
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    beta: Optional[float] = None
    dividend_yield: Optional[float] = None
    current_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None
    
    def __post_init__(self):
        self.current_value = self.current_price * self.quantity
        invested_amount = self.purchase_price * self.quantity
        self.profit_loss = self.current_value - invested_amount
        self.profit_loss_percent = (self.profit_loss / invested_amount * 100) if invested_amount > 0 else 0


@dataclass
class RebalancingAction:
    symbol: str
    action: str  # 'buy', 'sell', 'hold'
    current_allocation: float
    target_allocation: float
    allocation_difference: float
    current_value: float
    target_value: float
    value_difference: float
    suggested_quantity: int
    reason: str
    priority: int  # 1-5, where 1 is highest priority


@dataclass
class PortfolioAnalysis:
    total_value: float
    total_invested: float
    total_profit_loss: float
    total_profit_loss_percent: float
    risk_score: float
    sharpe_ratio: Optional[float]
    sector_allocation: Dict[str, float]
    risk_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]


class PortfolioRebalancingEngine:
    """Advanced portfolio rebalancing and optimization engine"""
    
    def __init__(self):
        self.ideal_allocations = {
            RiskTolerance.CONSERVATIVE: {
                'large_cap': 0.60,
                'mid_cap': 0.25,
                'small_cap': 0.10,
                'bonds_debt': 0.05
            },
            RiskTolerance.MODERATE: {
                'large_cap': 0.50,
                'mid_cap': 0.30,
                'small_cap': 0.15,
                'bonds_debt': 0.05
            },
            RiskTolerance.AGGRESSIVE: {
                'large_cap': 0.40,
                'mid_cap': 0.35,
                'small_cap': 0.20,
                'bonds_debt': 0.05
            }
        }
        
        self.sector_limits = {
            'Technology': 0.25,
            'Banking': 0.20,
            'Healthcare': 0.15,
            'Consumer': 0.15,
            'Energy': 0.10,
            'Others': 0.15
        }
        
        self.rebalancing_threshold = 0.05  # 5% deviation triggers rebalancing
    
    async def analyze_portfolio(self, stocks: List[Stock]) -> PortfolioAnalysis:
        """Comprehensive portfolio analysis"""
        
        if not stocks:
            return PortfolioAnalysis(0, 0, 0, 0, 0, None, {}, {}, {})
        
        # Calculate basic metrics
        total_value = sum(stock.current_value for stock in stocks)
        total_invested = sum(stock.purchase_price * stock.quantity for stock in stocks)
        total_profit_loss = total_value - total_invested
        total_profit_loss_percent = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        
        # Sector allocation
        sector_allocation = {}
        for stock in stocks:
            sector = stock.sector or 'Others'
            sector_allocation[sector] = sector_allocation.get(sector, 0) + stock.current_value
        
        # Convert to percentages
        sector_allocation = {sector: (value / total_value * 100) for sector, value in sector_allocation.items()}
        
        # Risk metrics
        risk_metrics = await self._calculate_risk_metrics(stocks)
        
        # Performance metrics
        performance_metrics = await self._calculate_performance_metrics(stocks)
        
        # Overall risk score
        risk_score = await self._calculate_portfolio_risk_score(stocks, sector_allocation)
        
        # Sharpe ratio (simplified calculation)
        sharpe_ratio = await self._calculate_sharpe_ratio(stocks)
        
        return PortfolioAnalysis(
            total_value=total_value,
            total_invested=total_invested,
            total_profit_loss=total_profit_loss,
            total_profit_loss_percent=total_profit_loss_percent,
            risk_score=risk_score,
            sharpe_ratio=sharpe_ratio,
            sector_allocation=sector_allocation,
            risk_metrics=risk_metrics,
            performance_metrics=performance_metrics
        )
    
    async def generate_rebalancing_suggestions(
        self,
        stocks: List[Stock],
        strategy: RebalancingStrategy = RebalancingStrategy.EQUAL_WEIGHT,
        risk_tolerance: RiskTolerance = RiskTolerance.MODERATE,
        available_cash: float = 0,
        max_trades: int = 10
    ) -> List[RebalancingAction]:
        """Generate comprehensive rebalancing suggestions"""
        
        if not stocks:
            return []
        
        portfolio_analysis = await self.analyze_portfolio(stocks)
        suggestions = []
        
        # Calculate target allocations based on strategy
        target_allocations = await self._calculate_target_allocations(
            stocks, strategy, risk_tolerance
        )
        
        # Current allocations
        current_allocations = {
            stock.symbol: (stock.current_value / portfolio_analysis.total_value)
            for stock in stocks
        }
        
        # Generate actions
        for stock in stocks:
            current_alloc = current_allocations[stock.symbol]
            target_alloc = target_allocations.get(stock.symbol, current_alloc)
            
            allocation_diff = target_alloc - current_alloc
            value_diff = allocation_diff * portfolio_analysis.total_value
            
            # Determine action
            if abs(allocation_diff) > self.rebalancing_threshold:
                if allocation_diff > 0:
                    action = "buy"
                    suggested_quantity = int(abs(value_diff) / stock.current_price)
                    reason = f"Underweight by {abs(allocation_diff):.1%} - increase position"
                else:
                    action = "sell"
                    suggested_quantity = int(abs(value_diff) / stock.current_price)
                    reason = f"Overweight by {abs(allocation_diff):.1%} - reduce position"
                
                priority = min(5, max(1, int(abs(allocation_diff) * 20)))  # 1-5 scale
            else:
                action = "hold"
                suggested_quantity = 0
                reason = "Allocation within acceptable range"
                priority = 5
            
            suggestion = RebalancingAction(
                symbol=stock.symbol,
                action=action,
                current_allocation=current_alloc,
                target_allocation=target_alloc,
                allocation_difference=allocation_diff,
                current_value=stock.current_value,
                target_value=target_alloc * portfolio_analysis.total_value,
                value_difference=value_diff,
                suggested_quantity=suggested_quantity,
                reason=reason,
                priority=priority
            )
            
            suggestions.append(suggestion)
        
        # Sort by priority and limit number of trades
        suggestions.sort(key=lambda x: (x.priority, abs(x.allocation_difference)), reverse=True)
        
        # Add sector-based suggestions
        sector_suggestions = await self._generate_sector_rebalancing(
            stocks, portfolio_analysis.sector_allocation
        )
        suggestions.extend(sector_suggestions)
        
        # Add risk-based suggestions
        risk_suggestions = await self._generate_risk_based_suggestions(
            stocks, portfolio_analysis, risk_tolerance
        )
        suggestions.extend(risk_suggestions)
        
        return suggestions[:max_trades]
    
    async def _calculate_target_allocations(
        self,
        stocks: List[Stock],
        strategy: RebalancingStrategy,
        risk_tolerance: RiskTolerance
    ) -> Dict[str, float]:
        """Calculate target allocations based on strategy"""
        
        if strategy == RebalancingStrategy.EQUAL_WEIGHT:
            return {stock.symbol: 1.0 / len(stocks) for stock in stocks}
        
        elif strategy == RebalancingStrategy.MARKET_CAP_WEIGHT:
            total_market_cap = sum(stock.market_cap or 1000000 for stock in stocks)
            return {
                stock.symbol: (stock.market_cap or 1000000) / total_market_cap
                for stock in stocks
            }
        
        elif strategy == RebalancingStrategy.RISK_PARITY:
            # Simplified risk parity - inverse of beta
            betas = [1.0 / (stock.beta or 1.0) for stock in stocks]
            total_inv_beta = sum(betas)
            
            return {
                stock.symbol: (1.0 / (stock.beta or 1.0)) / total_inv_beta
                for stock in stocks
            }
        
        elif strategy == RebalancingStrategy.MOMENTUM:
            # Based on recent performance
            performances = [stock.profit_loss_percent for stock in stocks]
            positive_performances = [max(0, perf) for perf in performances]
            total_positive = sum(positive_performances)
            
            if total_positive > 0:
                return {
                    stock.symbol: max(0, stock.profit_loss_percent) / total_positive
                    for stock in stocks
                }
            else:
                return {stock.symbol: 1.0 / len(stocks) for stock in stocks}
        
        elif strategy == RebalancingStrategy.VALUE:
            # Based on P/E ratios (inverse)
            pe_scores = [1.0 / (stock.pe_ratio or 15.0) for stock in stocks]
            total_pe_score = sum(pe_scores)
            
            return {
                stock.symbol: (1.0 / (stock.pe_ratio or 15.0)) / total_pe_score
                for stock in stocks
            }
        
        elif strategy == RebalancingStrategy.QUALITY:
            # Based on combination of metrics
            quality_scores = []
            for stock in stocks:
                score = 0
                if stock.pe_ratio and stock.pe_ratio < 20:
                    score += 1
                if stock.dividend_yield and stock.dividend_yield > 2:
                    score += 1
                if stock.profit_loss_percent > 0:
                    score += 1
                quality_scores.append(max(1, score))
            
            total_quality = sum(quality_scores)
            return {
                stock.symbol: quality_scores[i] / total_quality
                for i, stock in enumerate(stocks)
            }
        
        else:  # CUSTOM or default
            return {stock.symbol: 1.0 / len(stocks) for stock in stocks}
    
    async def _calculate_risk_metrics(self, stocks: List[Stock]) -> Dict[str, float]:
        """Calculate portfolio risk metrics"""
        
        if not stocks:
            return {}
        
        # Portfolio beta
        betas = [stock.beta or 1.0 for stock in stocks]
        weights = [stock.current_value for stock in stocks]
        total_value = sum(weights)
        weighted_betas = [beta * (weight / total_value) for beta, weight in zip(betas, weights)]
        portfolio_beta = sum(weighted_betas)
        
        # Concentration risk
        max_position = max(stock.current_value for stock in stocks) / total_value
        concentration_risk = min(10, max_position * 10)  # 0-10 scale
        
        # Sector concentration
        sectors = {}
        for stock in stocks:
            sector = stock.sector or 'Others'
            sectors[sector] = sectors.get(sector, 0) + stock.current_value
        
        max_sector = max(sectors.values()) / total_value
        sector_concentration_risk = min(10, max_sector * 10)
        
        return {
            'portfolio_beta': portfolio_beta,
            'concentration_risk': concentration_risk,
            'sector_concentration_risk': sector_concentration_risk,
            'number_of_positions': len(stocks),
            'diversification_ratio': min(10, len(stocks) / 2)  # Better with more stocks
        }
    
    async def _calculate_performance_metrics(self, stocks: List[Stock]) -> Dict[str, float]:
        """Calculate portfolio performance metrics"""
        
        if not stocks:
            return {}
        
        total_value = sum(stock.current_value for stock in stocks)
        total_invested = sum(stock.purchase_price * stock.quantity for stock in stocks)
        
        # Weighted average performance
        performances = []
        weights = []
        
        for stock in stocks:
            performances.append(stock.profit_loss_percent)
            weights.append(stock.current_value / total_value)
        
        weighted_performance = sum(p * w for p, w in zip(performances, weights))
        
        # Best and worst performers
        best_performance = max(performances) if performances else 0
        worst_performance = min(performances) if performances else 0
        
        # Win rate
        winners = sum(1 for p in performances if p > 0)
        win_rate = (winners / len(performances)) * 100 if performances else 0
        
        return {
            'weighted_avg_return': weighted_performance,
            'best_performer': best_performance,
            'worst_performer': worst_performance,
            'win_rate': win_rate,
            'total_return': ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
        }
    
    async def _calculate_portfolio_risk_score(self, stocks: List[Stock], sector_allocation: Dict[str, float]) -> float:
        """Calculate overall portfolio risk score (0-10)"""
        
        risk_score = 5.0  # Base score
        
        # Concentration risk
        max_sector = max(sector_allocation.values()) if sector_allocation else 0
        if max_sector > 50:
            risk_score += 2.0
        elif max_sector > 30:
            risk_score += 1.0
        
        # Number of positions
        if len(stocks) < 5:
            risk_score += 1.5
        elif len(stocks) < 10:
            risk_score += 0.5
        
        # Beta risk
        avg_beta = np.mean([stock.beta or 1.0 for stock in stocks])
        if avg_beta > 1.5:
            risk_score += 1.0
        elif avg_beta > 1.2:
            risk_score += 0.5
        
        return min(10.0, max(0.0, risk_score))
    
    async def _calculate_sharpe_ratio(self, stocks: List[Stock]) -> Optional[float]:
        """Calculate simplified Sharpe ratio"""
        
        if not stocks:
            return None
        
        # Simplified calculation using returns and assumed risk-free rate
        returns = [stock.profit_loss_percent / 100 for stock in stocks]
        avg_return = np.mean(returns)
        std_return = np.std(returns) if len(returns) > 1 else 0.1
        risk_free_rate = 0.06  # 6% assumed risk-free rate
        
        if std_return == 0:
            return None
        
        return (avg_return - risk_free_rate) / std_return
    
    async def _generate_sector_rebalancing(
        self,
        stocks: List[Stock],
        current_sector_allocation: Dict[str, float]
    ) -> List[RebalancingAction]:
        """Generate sector-based rebalancing suggestions"""
        
        suggestions = []
        
        for sector, current_percent in current_sector_allocation.items():
            ideal_percent = self.sector_limits.get(sector, 15.0)  # 15% default
            
            if current_percent > ideal_percent + 5:  # Overweight
                # Find stocks in this sector to potentially sell
                sector_stocks = [s for s in stocks if s.sector == sector]
                if sector_stocks:
                    # Suggest selling the worst performer in the overweight sector
                    worst_performer = min(sector_stocks, key=lambda s: s.profit_loss_percent)
                    
                    suggestion = RebalancingAction(
                        symbol=worst_performer.symbol,
                        action="sell",
                        current_allocation=current_percent / 100,
                        target_allocation=ideal_percent / 100,
                        allocation_difference=(ideal_percent - current_percent) / 100,
                        current_value=worst_performer.current_value,
                        target_value=0,  # Sector level adjustment
                        value_difference=0,
                        suggested_quantity=int(worst_performer.quantity * 0.2),  # Sell 20%
                        reason=f"Sector {sector} overweight ({current_percent:.1f}% vs target {ideal_percent:.1f}%)",
                        priority=2
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    async def _generate_risk_based_suggestions(
        self,
        stocks: List[Stock],
        portfolio_analysis: PortfolioAnalysis,
        risk_tolerance: RiskTolerance
    ) -> List[RebalancingAction]:
        """Generate risk-based rebalancing suggestions"""
        
        suggestions = []
        
        # High concentration risk
        if portfolio_analysis.risk_metrics.get('concentration_risk', 0) > 7:
            # Find the largest position
            largest_stock = max(stocks, key=lambda s: s.current_value)
            total_value = sum(s.current_value for s in stocks)
            
            if largest_stock.current_value / total_value > 0.3:  # More than 30%
                suggestion = RebalancingAction(
                    symbol=largest_stock.symbol,
                    action="sell",
                    current_allocation=largest_stock.current_value / total_value,
                    target_allocation=0.20,  # Target 20%
                    allocation_difference=-0.10,
                    current_value=largest_stock.current_value,
                    target_value=total_value * 0.20,
                    value_difference=-(largest_stock.current_value - total_value * 0.20),
                    suggested_quantity=int(largest_stock.quantity * 0.3),  # Sell 30%
                    reason="Reduce concentration risk - position too large",
                    priority=1
                )
                suggestions.append(suggestion)
        
        # Risk tolerance mismatch
        if risk_tolerance == RiskTolerance.CONSERVATIVE and portfolio_analysis.risk_score > 7:
            # Suggest reducing high-beta stocks
            high_beta_stocks = [s for s in stocks if (s.beta or 1.0) > 1.5]
            for stock in high_beta_stocks[:2]:  # Top 2 high-beta stocks
                suggestion = RebalancingAction(
                    symbol=stock.symbol,
                    action="sell",
                    current_allocation=stock.current_value / portfolio_analysis.total_value,
                    target_allocation=(stock.current_value / portfolio_analysis.total_value) * 0.5,
                    allocation_difference=-0.05,
                    current_value=stock.current_value,
                    target_value=stock.current_value * 0.5,
                    value_difference=-stock.current_value * 0.5,
                    suggested_quantity=int(stock.quantity * 0.5),  # Sell 50%
                    reason=f"High beta ({stock.beta:.1f}) - reduce for conservative portfolio",
                    priority=2
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    async def generate_tax_efficient_rebalancing(
        self,
        stocks: List[Stock],
        target_allocations: Dict[str, float]
    ) -> List[RebalancingAction]:
        """Generate tax-efficient rebalancing suggestions"""
        
        suggestions = []
        current_date = datetime.now()
        
        for stock in stocks:
            purchase_date = datetime.fromisoformat(stock.purchase_date)
            days_held = (current_date - purchase_date).days
            
            target_alloc = target_allocations.get(stock.symbol, 0)
            current_alloc = stock.current_value / sum(s.current_value for s in stocks)
            
            if abs(target_alloc - current_alloc) > self.rebalancing_threshold:
                # Tax considerations
                if days_held < 365 and stock.profit_loss > 0:  # Short-term gains
                    reason = f"Consider waiting {365 - days_held} days for LTCG treatment"
                    priority = 4  # Lower priority due to tax implications
                elif days_held >= 365 and stock.profit_loss > 100000:  # LTCG > 1 lakh
                    reason = "LTCG tax applicable on gains > ₹1 lakh"
                    priority = 3
                elif stock.profit_loss < 0:  # Loss harvesting opportunity
                    reason = "Tax loss harvesting - offset gains with losses"
                    priority = 2
                else:
                    reason = "Standard rebalancing"
                    priority = 3
                
                action = "sell" if current_alloc > target_alloc else "buy"
                
                suggestion = RebalancingAction(
                    symbol=stock.symbol,
                    action=action,
                    current_allocation=current_alloc,
                    target_allocation=target_alloc,
                    allocation_difference=target_alloc - current_alloc,
                    current_value=stock.current_value,
                    target_value=0,  # Calculate separately
                    value_difference=0,
                    suggested_quantity=0,  # Calculate separately
                    reason=reason,
                    priority=priority
                )
                
                suggestions.append(suggestion)
        
        return suggestions
    
    def export_analysis_to_json(self, analysis: PortfolioAnalysis, suggestions: List[RebalancingAction]) -> str:
        """Export analysis and suggestions to JSON"""
        
        data = {
            'analysis': asdict(analysis),
            'suggestions': [asdict(suggestion) for suggestion in suggestions],
            'generated_at': datetime.now().isoformat(),
            'rebalancing_threshold': self.rebalancing_threshold
        }
        
        return json.dumps(data, indent=2, default=str)
    
    def calculate_implementation_cost(
        self,
        suggestions: List[RebalancingAction],
        brokerage_rate: float = 0.001
    ) -> Dict[str, float]:
        """Calculate cost of implementing rebalancing suggestions"""
        
        total_transaction_value = 0
        total_brokerage = 0
        
        for suggestion in suggestions:
            if suggestion.action in ['buy', 'sell']:
                transaction_value = abs(suggestion.value_difference)
                brokerage = transaction_value * brokerage_rate
                
                total_transaction_value += transaction_value
                total_brokerage += brokerage
        
        return {
            'total_transaction_value': total_transaction_value,
            'total_brokerage_cost': total_brokerage,
            'cost_as_percentage': (total_brokerage / total_transaction_value * 100) if total_transaction_value > 0 else 0,
            'number_of_transactions': len([s for s in suggestions if s.action in ['buy', 'sell']])
        }


# Example usage and testing
async def test_portfolio_rebalancer():
    """Test the portfolio rebalancing engine"""
    
    # Create sample portfolio
    sample_stocks = [
        Stock("RELIANCE", 2500, 10, 2300, "2023-01-15", "Energy", 15000000, 12, 1.2, 2.5),
        Stock("TCS", 3200, 15, 3000, "2023-02-01", "Technology", 12000000, 22, 0.8, 1.8),
        Stock("INFY", 1400, 20, 1200, "2023-03-01", "Technology", 6000000, 18, 0.9, 2.0),
        Stock("HDFC", 1600, 25, 1500, "2023-01-20", "Banking", 8000000, 15, 1.1, 3.2),
        Stock("ITC", 350, 50, 320, "2023-04-01", "Consumer", 4500000, 14, 0.6, 4.5),
    ]
    
    # Create rebalancing engine
    rebalancer = PortfolioRebalancingEngine()
    
    # Analyze portfolio
    print("=== Portfolio Analysis ===")
    analysis = await rebalancer.analyze_portfolio(sample_stocks)
    print(f"Total Value: ₹{analysis.total_value:,.2f}")
    print(f"Total P&L: ₹{analysis.total_profit_loss:,.2f} ({analysis.total_profit_loss_percent:.1f}%)")
    print(f"Risk Score: {analysis.risk_score:.1f}/10")
    print(f"Sharpe Ratio: {analysis.sharpe_ratio:.2f}" if analysis.sharpe_ratio else "N/A")
    
    print("\nSector Allocation:")
    for sector, allocation in analysis.sector_allocation.items():
        print(f"  {sector}: {allocation:.1f}%")
    
    # Generate rebalancing suggestions
    print("\n=== Rebalancing Suggestions ===")
    
    strategies = [
        RebalancingStrategy.EQUAL_WEIGHT,
        RebalancingStrategy.MARKET_CAP_WEIGHT,
        RebalancingStrategy.RISK_PARITY
    ]
    
    for strategy in strategies:
        print(f"\n--- {strategy.value.upper()} Strategy ---")
        suggestions = await rebalancer.generate_rebalancing_suggestions(
            sample_stocks, strategy, RiskTolerance.MODERATE
        )
        
        for suggestion in suggestions[:5]:  # Show top 5
            print(f"{suggestion.symbol}: {suggestion.action.upper()} "
                  f"(Current: {suggestion.current_allocation:.1%}, "
                  f"Target: {suggestion.target_allocation:.1%}) "
                  f"- {suggestion.reason}")
    
    # Tax-efficient rebalancing
    print("\n=== Tax-Efficient Rebalancing ===")
    target_allocations = {stock.symbol: 0.20 for stock in sample_stocks}  # Equal weight
    tax_suggestions = await rebalancer.generate_tax_efficient_rebalancing(
        sample_stocks, target_allocations
    )
    
    for suggestion in tax_suggestions:
        print(f"{suggestion.symbol}: {suggestion.action.upper()} - {suggestion.reason}")
    
    # Implementation cost
    print("\n=== Implementation Cost Analysis ===")
    cost_analysis = rebalancer.calculate_implementation_cost(suggestions)
    print(f"Total Transaction Value: ₹{cost_analysis['total_transaction_value']:,.2f}")
    print(f"Total Brokerage Cost: ₹{cost_analysis['total_brokerage_cost']:,.2f}")
    print(f"Cost as % of transaction: {cost_analysis['cost_as_percentage']:.3f}%")
    
    # Export to JSON
    json_data = rebalancer.export_analysis_to_json(analysis, suggestions)
    print(f"\nExported data: {len(json_data)} characters")


if __name__ == "__main__":
    asyncio.run(test_portfolio_rebalancer())