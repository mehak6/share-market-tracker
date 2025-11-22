"""
Tax Optimization Strategies Module
Advanced tax planning and optimization for Indian stock market investors
"""

import json
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import calendar
import asyncio


class TaxRegime(Enum):
    OLD = "old_regime"
    NEW = "new_regime"


class InvestmentType(Enum):
    EQUITY = "equity"
    EQUITY_MUTUAL_FUND = "equity_mutual_fund"
    DEBT_MUTUAL_FUND = "debt_mutual_fund"
    BONDS = "bonds"
    FD = "fixed_deposit"
    ELSS = "elss"


class CapitalGainType(Enum):
    STCG = "short_term"  # < 1 year
    LTCG = "long_term"   # >= 1 year


@dataclass
class TaxLiability:
    stcg_amount: float
    stcg_tax: float
    ltcg_amount: float
    ltcg_tax: float
    total_tax: float
    tax_rate_used: Dict[str, float]


@dataclass
class HoldingTaxInfo:
    symbol: str
    quantity: int
    purchase_date: date
    purchase_price: float
    current_price: float
    holding_period_days: int
    gain_loss_amount: float
    gain_loss_percentage: float
    capital_gain_type: CapitalGainType
    tax_liability: float
    days_to_ltcg: Optional[int] = None


@dataclass
class TaxOptimizationStrategy:
    strategy_name: str
    description: str
    potential_tax_saving: float
    implementation_steps: List[str]
    timeline: str
    risk_level: str
    priority: int  # 1-5, where 1 is highest


@dataclass
class TaxHarvestingOpportunity:
    sell_symbol: str
    sell_quantity: int
    sell_value: float
    loss_amount: float
    buy_symbol: Optional[str]
    buy_quantity: Optional[int]
    net_tax_benefit: float
    wash_sale_risk: bool
    description: str


class IndianTaxOptimizer:
    """Advanced tax optimization for Indian stock market investors"""
    
    def __init__(self, financial_year: int = None):
        self.financial_year = financial_year or self._get_current_financial_year()
        
        # Indian tax rates (2024-25)
        self.tax_rates = {
            'stcg_equity': 0.156,      # 15% + 4% cess
            'ltcg_equity': 0.104,      # 10% + 4% cess (on gains > 1 lakh)
            'stcg_debt': 0.312,        # As per income tax slab + 4% cess
            'ltcg_debt': 0.208,        # 20% + 4% cess with indexation
            'dividend': 0.104,         # 10% + 4% cess (if > 5000 per company)
            'ltcg_exemption_limit': 100000  # ₹1 lakh exemption for equity LTCG
        }
        
        # Tax saving instruments limits
        self.tax_saving_limits = {
            'section_80c': 150000,      # ELSS, PPF, etc.
            'section_80d': 25000,       # Health insurance
            'nps_80ccd1b': 50000,       # Additional NPS
            'section_80tta': 10000,     # Savings account interest
            'section_80ttb': 50000      # Senior citizen savings interest
        }
        
        self.current_date = datetime.now().date()
    
    def _get_current_financial_year(self) -> int:
        """Get current Indian financial year"""
        today = datetime.now().date()
        if today.month >= 4:  # April onwards
            return today.year
        else:
            return today.year - 1
    
    async def analyze_portfolio_tax_implications(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Comprehensive tax analysis of portfolio"""
        
        tax_holdings = []
        total_stcg_gains = 0
        total_ltcg_gains = 0
        total_stcg_losses = 0
        total_ltcg_losses = 0
        
        for holding in holdings:
            tax_info = self._calculate_holding_tax_info(holding)
            tax_holdings.append(tax_info)
            
            if tax_info.gain_loss_amount > 0:  # Gains
                if tax_info.capital_gain_type == CapitalGainType.STCG:
                    total_stcg_gains += tax_info.gain_loss_amount
                else:
                    total_ltcg_gains += tax_info.gain_loss_amount
            else:  # Losses
                if tax_info.capital_gain_type == CapitalGainType.STCG:
                    total_stcg_losses += abs(tax_info.gain_loss_amount)
                else:
                    total_ltcg_losses += abs(tax_info.gain_loss_amount)
        
        # Calculate net gains after offsetting losses
        net_stcg_gains = max(0, total_stcg_gains - total_stcg_losses)
        net_ltcg_gains = max(0, total_ltcg_gains - total_ltcg_losses)
        
        # Calculate tax liability
        current_tax_liability = self._calculate_tax_liability(net_stcg_gains, net_ltcg_gains)
        
        # Unrealized tax liability (if sold today)
        unrealized_gains = sum(max(0, h.gain_loss_amount) for h in tax_holdings)
        unrealized_losses = sum(abs(min(0, h.gain_loss_amount)) for h in tax_holdings)
        
        return {
            'holdings_analysis': [asdict(h) for h in tax_holdings],
            'realized_gains_losses': {
                'stcg_gains': total_stcg_gains,
                'stcg_losses': total_stcg_losses,
                'ltcg_gains': total_ltcg_gains,
                'ltcg_losses': total_ltcg_losses,
                'net_stcg_gains': net_stcg_gains,
                'net_ltcg_gains': net_ltcg_gains
            },
            'tax_liability': asdict(current_tax_liability),
            'unrealized_analysis': {
                'unrealized_gains': unrealized_gains,
                'unrealized_losses': unrealized_losses,
                'potential_tax_if_sold_today': self._calculate_unrealized_tax_liability(tax_holdings)
            },
            'financial_year': self.financial_year,
            'analysis_date': self.current_date.isoformat()
        }
    
    def _calculate_holding_tax_info(self, holding: Dict) -> HoldingTaxInfo:
        """Calculate tax information for a single holding"""
        
        symbol = holding['symbol']
        quantity = holding['quantity']
        purchase_price = holding['purchase_price']
        current_price = holding['current_price']
        purchase_date_str = holding['purchase_date']
        
        # Parse purchase date
        if isinstance(purchase_date_str, str):
            purchase_date = datetime.fromisoformat(purchase_date_str).date()
        else:
            purchase_date = purchase_date_str
        
        # Calculate holding period
        holding_period_days = (self.current_date - purchase_date).days
        
        # Determine capital gain type
        capital_gain_type = CapitalGainType.LTCG if holding_period_days >= 365 else CapitalGainType.STCG
        
        # Calculate gain/loss
        invested_amount = purchase_price * quantity
        current_value = current_price * quantity
        gain_loss_amount = current_value - invested_amount
        gain_loss_percentage = (gain_loss_amount / invested_amount * 100) if invested_amount > 0 else 0
        
        # Calculate tax liability
        tax_liability = 0
        if gain_loss_amount > 0:  # Only gains are taxable
            if capital_gain_type == CapitalGainType.STCG:
                tax_liability = gain_loss_amount * self.tax_rates['stcg_equity']
            else:  # LTCG
                taxable_ltcg = max(0, gain_loss_amount - self.tax_rates['ltcg_exemption_limit'])
                tax_liability = taxable_ltcg * self.tax_rates['ltcg_equity']
        
        # Days to LTCG (if currently STCG)
        days_to_ltcg = None
        if capital_gain_type == CapitalGainType.STCG:
            days_to_ltcg = 365 - holding_period_days
        
        return HoldingTaxInfo(
            symbol=symbol,
            quantity=quantity,
            purchase_date=purchase_date,
            purchase_price=purchase_price,
            current_price=current_price,
            holding_period_days=holding_period_days,
            gain_loss_amount=gain_loss_amount,
            gain_loss_percentage=gain_loss_percentage,
            capital_gain_type=capital_gain_type,
            tax_liability=tax_liability,
            days_to_ltcg=days_to_ltcg
        )
    
    def _calculate_tax_liability(self, stcg_gains: float, ltcg_gains: float) -> TaxLiability:
        """Calculate total tax liability"""
        
        # STCG tax
        stcg_tax = stcg_gains * self.tax_rates['stcg_equity']
        
        # LTCG tax (with exemption)
        taxable_ltcg = max(0, ltcg_gains - self.tax_rates['ltcg_exemption_limit'])
        ltcg_tax = taxable_ltcg * self.tax_rates['ltcg_equity']
        
        total_tax = stcg_tax + ltcg_tax
        
        return TaxLiability(
            stcg_amount=stcg_gains,
            stcg_tax=stcg_tax,
            ltcg_amount=ltcg_gains,
            ltcg_tax=ltcg_tax,
            total_tax=total_tax,
            tax_rate_used={
                'stcg_rate': self.tax_rates['stcg_equity'],
                'ltcg_rate': self.tax_rates['ltcg_equity'],
                'ltcg_exemption': self.tax_rates['ltcg_exemption_limit']
            }
        )
    
    def _calculate_unrealized_tax_liability(self, holdings: List[HoldingTaxInfo]) -> float:
        """Calculate tax liability if all positions were sold today"""
        
        total_stcg_gains = 0
        total_ltcg_gains = 0
        
        for holding in holdings:
            if holding.gain_loss_amount > 0:  # Only gains
                if holding.capital_gain_type == CapitalGainType.STCG:
                    total_stcg_gains += holding.gain_loss_amount
                else:
                    total_ltcg_gains += holding.gain_loss_amount
        
        tax_liability = self._calculate_tax_liability(total_stcg_gains, total_ltcg_gains)
        return tax_liability.total_tax
    
    async def generate_tax_optimization_strategies(
        self,
        portfolio_analysis: Dict,
        risk_tolerance: str = "moderate",
        available_cash: float = 0
    ) -> List[TaxOptimizationStrategy]:
        """Generate comprehensive tax optimization strategies"""
        
        strategies = []
        holdings_analysis = portfolio_analysis['holdings_analysis']
        unrealized_analysis = portfolio_analysis['unrealized_analysis']
        
        # Strategy 1: Tax Loss Harvesting
        loss_harvesting = await self._tax_loss_harvesting_strategy(holdings_analysis)
        if loss_harvesting:
            strategies.append(loss_harvesting)
        
        # Strategy 2: Hold for LTCG
        ltcg_strategy = await self._hold_for_ltcg_strategy(holdings_analysis)
        if ltcg_strategy:
            strategies.append(ltcg_strategy)
        
        # Strategy 3: LTCG Exemption Optimization
        exemption_strategy = await self._ltcg_exemption_strategy(holdings_analysis)
        if exemption_strategy:
            strategies.append(exemption_strategy)
        
        # Strategy 4: Systematic Profit Booking
        profit_booking = await self._systematic_profit_booking_strategy(holdings_analysis)
        if profit_booking:
            strategies.append(profit_booking)
        
        # Strategy 5: Tax Saving Investments
        tax_saving_strategy = await self._tax_saving_investments_strategy(available_cash)
        strategies.append(tax_saving_strategy)
        
        # Strategy 6: Dividend vs Capital Gains
        dividend_strategy = await self._dividend_optimization_strategy(holdings_analysis)
        if dividend_strategy:
            strategies.append(dividend_strategy)
        
        # Sort by priority
        strategies.sort(key=lambda x: x.priority)
        
        return strategies
    
    async def _tax_loss_harvesting_strategy(self, holdings: List[Dict]) -> Optional[TaxOptimizationStrategy]:
        """Generate tax loss harvesting strategy"""
        
        losing_positions = [h for h in holdings if h['gain_loss_amount'] < 0]
        gaining_positions = [h for h in holdings if h['gain_loss_amount'] > 0]
        
        if not losing_positions or not gaining_positions:
            return None
        
        total_losses = sum(abs(h['gain_loss_amount']) for h in losing_positions)
        total_gains = sum(h['gain_loss_amount'] for h in gaining_positions)
        
        harvestable_losses = min(total_losses, total_gains)
        potential_tax_saving = harvestable_losses * self.tax_rates['stcg_equity']
        
        if potential_tax_saving < 1000:  # Minimum threshold
            return None
        
        steps = [
            "1. Identify losing positions that can offset current year gains",
            "2. Sell losing positions to realize capital losses",
            "3. Avoid wash sale rules (don't repurchase same stock within 30 days)",
            "4. Consider reinvesting in similar but different stocks",
            f"5. Book profits in gaining positions up to loss amount (₹{harvestable_losses:,.0f})"
        ]
        
        return TaxOptimizationStrategy(
            strategy_name="Tax Loss Harvesting",
            description=f"Offset capital gains with capital losses to reduce tax liability by ₹{potential_tax_saving:,.0f}",
            potential_tax_saving=potential_tax_saving,
            implementation_steps=steps,
            timeline="Before March 31st",
            risk_level="Low",
            priority=1
        )
    
    async def _hold_for_ltcg_strategy(self, holdings: List[Dict]) -> Optional[TaxOptimizationStrategy]:
        """Strategy to hold STCG positions for LTCG treatment"""
        
        stcg_winners = [h for h in holdings 
                       if h['capital_gain_type'] == 'short_term' 
                       and h['gain_loss_amount'] > 0 
                       and h['days_to_ltcg'] and h['days_to_ltcg'] < 180]  # Within 6 months
        
        if not stcg_winners:
            return None
        
        total_stcg_gains = sum(h['gain_loss_amount'] for h in stcg_winners)
        
        # Tax difference
        stcg_tax = total_stcg_gains * self.tax_rates['stcg_equity']
        ltcg_tax = max(0, total_stcg_gains - self.tax_rates['ltcg_exemption_limit']) * self.tax_rates['ltcg_equity']
        tax_saving = stcg_tax - ltcg_tax
        
        if tax_saving < 5000:  # Minimum threshold
            return None
        
        avg_days_to_wait = sum(h['days_to_ltcg'] for h in stcg_winners) / len(stcg_winners)
        
        steps = [
            f"1. Hold {len(stcg_winners)} winning positions for LTCG treatment",
            f"2. Average waiting period: {avg_days_to_wait:.0f} days",
            "3. Monitor positions for significant price changes",
            "4. Consider stop-loss if positions decline significantly",
            "5. Sell after completing 1 year holding period"
        ]
        
        return TaxOptimizationStrategy(
            strategy_name="Hold for LTCG Treatment",
            description=f"Wait for LTCG status to reduce tax from 15.6% to 10.4% on gains",
            potential_tax_saving=tax_saving,
            implementation_steps=steps,
            timeline=f"Next {avg_days_to_wait:.0f} days",
            risk_level="Medium",
            priority=2
        )
    
    async def _ltcg_exemption_strategy(self, holdings: List[Dict]) -> Optional[TaxOptimizationStrategy]:
        """Strategy to optimize LTCG exemption usage"""
        
        ltcg_positions = [h for h in holdings 
                         if h['capital_gain_type'] == 'long_term' 
                         and h['gain_loss_amount'] > 0]
        
        if not ltcg_positions:
            return None
        
        total_ltcg_gains = sum(h['gain_loss_amount'] for h in ltcg_positions)
        
        if total_ltcg_gains <= self.tax_rates['ltcg_exemption_limit']:
            return None
        
        # Calculate optimal booking
        exemption_amount = self.tax_rates['ltcg_exemption_limit']
        excess_gains = total_ltcg_gains - exemption_amount
        
        # Find positions to book within exemption
        positions_to_book = []
        running_total = 0
        
        # Sort by smallest gains first to optimize exemption usage
        sorted_positions = sorted(ltcg_positions, key=lambda x: x['gain_loss_amount'])
        
        for position in sorted_positions:
            if running_total + position['gain_loss_amount'] <= exemption_amount:
                positions_to_book.append(position)
                running_total += position['gain_loss_amount']
        
        if not positions_to_book:
            return None
        
        tax_saving = running_total * self.tax_rates['ltcg_equity']  # Tax saved by using exemption
        
        steps = [
            f"1. Book profits in {len(positions_to_book)} LTCG positions",
            f"2. Total gains to book: ₹{running_total:,.0f} (within ₹1 lakh exemption)",
            "3. No tax liability on these gains",
            "4. Consider reinvesting in different stocks for continued growth",
            "5. Plan similar strategy for next financial year"
        ]
        
        return TaxOptimizationStrategy(
            strategy_name="LTCG Exemption Optimization",
            description=f"Use ₹1 lakh LTCG exemption to book tax-free profits",
            potential_tax_saving=tax_saving,
            implementation_steps=steps,
            timeline="Current financial year",
            risk_level="Low",
            priority=2
        )
    
    async def _systematic_profit_booking_strategy(self, holdings: List[Dict]) -> Optional[TaxOptimizationStrategy]:
        """Strategy for systematic profit booking across financial years"""
        
        high_gain_positions = [h for h in holdings if h['gain_loss_percentage'] > 50]
        
        if not high_gain_positions:
            return None
        
        total_high_gains = sum(h['gain_loss_amount'] for h in high_gain_positions)
        
        # Spread across multiple years
        yearly_booking = total_high_gains / 3  # Spread over 3 years
        annual_tax_saving = yearly_booking * 0.05  # Approximate saving by spreading
        
        steps = [
            "1. Identify positions with >50% gains for systematic booking",
            "2. Book 1/3rd of profits in current financial year",
            "3. Book another 1/3rd in next financial year",
            "4. Complete profit booking in third year",
            "5. Reinvest proceeds in diversified portfolio",
            "6. Use LTCG exemption optimally each year"
        ]
        
        return TaxOptimizationStrategy(
            strategy_name="Systematic Profit Booking",
            description=f"Spread profit booking across multiple years to optimize tax liability",
            potential_tax_saving=annual_tax_saving * 3,
            implementation_steps=steps,
            timeline="3 years",
            risk_level="Medium",
            priority=3
        )
    
    async def _tax_saving_investments_strategy(self, available_cash: float) -> TaxOptimizationStrategy:
        """Strategy for tax-saving investments"""
        
        max_80c_investment = min(available_cash, self.tax_saving_limits['section_80c'])
        potential_tax_saving = max_80c_investment * 0.30  # Assuming 30% tax bracket
        
        steps = [
            f"1. Invest ₹{max_80c_investment:,.0f} in ELSS mutual funds (Section 80C)",
            f"2. Consider additional ₹{self.tax_saving_limits['nps_80ccd1b']:,} in NPS (80CCD1B)",
            "3. Ensure health insurance premium payments (Section 80D)",
            "4. Optimize fixed deposit interest within limits",
            "5. Plan tax-saving investments at start of financial year"
        ]
        
        return TaxOptimizationStrategy(
            strategy_name="Tax-Saving Investments",
            description=f"Maximize deductions under various sections to reduce taxable income",
            potential_tax_saving=potential_tax_saving,
            implementation_steps=steps,
            timeline="Current financial year",
            risk_level="Low",
            priority=4
        )
    
    async def _dividend_optimization_strategy(self, holdings: List[Dict]) -> Optional[TaxOptimizationStrategy]:
        """Strategy to optimize dividend vs capital gains"""
        
        # This is a simplified analysis
        dividend_paying_stocks = [h for h in holdings if h.get('dividend_yield', 0) > 3]
        
        if not dividend_paying_stocks:
            return None
        
        steps = [
            "1. Analyze dividend yield vs capital appreciation potential",
            "2. Consider dividend tax (10% if >₹5,000 per company)",
            "3. Compare with capital gains tax implications",
            "4. Optimize portfolio between growth and dividend stocks",
            "5. Time dividend receipt to optimize tax impact"
        ]
        
        return TaxOptimizationStrategy(
            strategy_name="Dividend vs Capital Gains Optimization",
            description="Balance dividend income with capital gains for tax efficiency",
            potential_tax_saving=5000,  # Estimated
            implementation_steps=steps,
            timeline="Ongoing",
            risk_level="Low",
            priority=5
        )
    
    async def identify_tax_harvesting_opportunities(
        self,
        holdings: List[Dict],
        target_loss_amount: float = 0
    ) -> List[TaxHarvestingOpportunity]:
        """Identify specific tax harvesting opportunities"""
        
        opportunities = []
        
        losing_positions = [h for h in holdings if h['gain_loss_amount'] < -5000]  # Min ₹5K loss
        gaining_positions = [h for h in holdings if h['gain_loss_amount'] > 5000]   # Min ₹5K gain
        
        for losing_pos in losing_positions:
            loss_amount = abs(losing_pos['gain_loss_amount'])
            
            # Find similar gaining position to offset
            similar_gains = [g for g in gaining_positions 
                           if g['sector'] != losing_pos.get('sector', '')]  # Different sector
            
            if similar_gains:
                best_match = max(similar_gains, key=lambda x: x['gain_loss_amount'])
                
                # Calculate net benefit
                tax_benefit = min(loss_amount, best_match['gain_loss_amount']) * self.tax_rates['stcg_equity']
                
                opportunity = TaxHarvestingOpportunity(
                    sell_symbol=losing_pos['symbol'],
                    sell_quantity=losing_pos['quantity'],
                    sell_value=losing_pos['current_price'] * losing_pos['quantity'],
                    loss_amount=loss_amount,
                    buy_symbol=None,  # To be decided
                    buy_quantity=None,
                    net_tax_benefit=tax_benefit,
                    wash_sale_risk=False,  # Assuming different stock
                    description=f"Harvest loss from {losing_pos['symbol']} to offset gains"
                )
                
                opportunities.append(opportunity)
        
        return sorted(opportunities, key=lambda x: x.net_tax_benefit, reverse=True)
    
    def generate_year_end_tax_checklist(self) -> Dict[str, List[str]]:
        """Generate year-end tax planning checklist"""
        
        current_month = datetime.now().month
        
        if current_month >= 1 and current_month <= 3:  # Jan-Mar (end of FY)
            checklist_type = "year_end"
        else:
            checklist_type = "mid_year"
        
        checklists = {
            "year_end": {
                "Capital Gains Review": [
                    "Calculate total capital gains and losses for the year",
                    "Identify opportunities for tax loss harvesting",
                    "Book profits within LTCG exemption limit (₹1 lakh)",
                    "Plan any last-minute buy/sell decisions",
                    "Document all transactions for tax filing"
                ],
                "Tax Saving Investments": [
                    "Complete Section 80C investments (₹1.5 lakh limit)",
                    "Make additional NPS contribution (₹50,000 80CCD1B)",
                    "Pay health insurance premiums (80D)",
                    "Review and optimize all eligible deductions",
                    "Plan investments for next financial year"
                ],
                "Documentation": [
                    "Collect all transaction statements",
                    "Calculate exact capital gains with dates",
                    "Prepare Form 16 and other tax documents",
                    "Review dividend income and TDS",
                    "Organize all investment proofs"
                ]
            },
            "mid_year": {
                "Portfolio Review": [
                    "Analyze current gains/losses position",
                    "Identify stocks approaching 1-year holding period",
                    "Review sector allocation and concentration",
                    "Plan tax-efficient rebalancing",
                    "Monitor dividend announcements"
                ],
                "Tax Planning": [
                    "Start tax-saving investments early",
                    "Plan systematic profit booking strategy",
                    "Consider timing of major transactions",
                    "Review tax implications of any corporate actions",
                    "Plan for next year's tax strategy"
                ]
            }
        }
        
        return checklists.get(checklist_type, checklists["mid_year"])
    
    def calculate_holding_period_calendar(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Create a calendar view of when holdings become LTCG eligible"""
        
        ltcg_calendar = {}
        
        for holding in holdings:
            if holding.get('days_to_ltcg') and holding['days_to_ltcg'] > 0:
                purchase_date = datetime.fromisoformat(holding['purchase_date']).date()
                ltcg_date = purchase_date + timedelta(days=365)
                
                month_key = ltcg_date.strftime("%Y-%m")
                
                if month_key not in ltcg_calendar:
                    ltcg_calendar[month_key] = []
                
                ltcg_calendar[month_key].append({
                    'symbol': holding['symbol'],
                    'ltcg_date': ltcg_date.isoformat(),
                    'current_gain': holding['gain_loss_amount'],
                    'potential_tax_saving': holding['gain_loss_amount'] * 0.052  # 15.6% - 10.4%
                })
        
        return {
            'ltcg_calendar': ltcg_calendar,
            'total_positions_becoming_ltcg': sum(len(positions) for positions in ltcg_calendar.values()),
            'total_potential_tax_saving': sum(
                pos['potential_tax_saving'] for positions in ltcg_calendar.values() 
                for pos in positions
            )
        }
    
    def export_tax_report(self, portfolio_analysis: Dict, strategies: List[TaxOptimizationStrategy]) -> str:
        """Export comprehensive tax report"""
        
        report_data = {
            'report_type': 'Tax Optimization Report',
            'financial_year': f"{self.financial_year}-{self.financial_year + 1}",
            'generated_date': datetime.now().isoformat(),
            'portfolio_analysis': portfolio_analysis,
            'optimization_strategies': [asdict(strategy) for strategy in strategies],
            'tax_rates_used': self.tax_rates,
            'year_end_checklist': self.generate_year_end_tax_checklist(),
            'summary': {
                'total_current_tax_liability': portfolio_analysis['tax_liability']['total_tax'],
                'total_optimization_potential': sum(s.potential_tax_saving for s in strategies),
                'net_tax_after_optimization': portfolio_analysis['tax_liability']['total_tax'] - sum(s.potential_tax_saving for s in strategies)
            }
        }
        
        return json.dumps(report_data, indent=2, default=str)


# Example usage and testing
async def test_tax_optimizer():
    """Test the tax optimization system"""
    
    # Sample portfolio data
    sample_holdings = [
        {
            'symbol': 'RELIANCE',
            'quantity': 100,
            'purchase_price': 2200,
            'current_price': 2500,
            'purchase_date': '2023-06-15',
            'sector': 'Energy'
        },
        {
            'symbol': 'TCS',
            'quantity': 50,
            'purchase_price': 3500,
            'current_price': 3200,  # Loss position
            'purchase_date': '2024-01-10',
            'sector': 'Technology'
        },
        {
            'symbol': 'INFY',
            'quantity': 80,
            'purchase_price': 1200,
            'current_price': 1400,
            'purchase_date': '2022-05-20',  # LTCG eligible
            'sector': 'Technology'
        },
        {
            'symbol': 'HDFC',
            'quantity': 60,
            'purchase_price': 1400,
            'current_price': 1600,
            'purchase_date': '2024-08-01',  # Recent purchase
            'sector': 'Banking'
        }
    ]
    
    # Create tax optimizer
    tax_optimizer = IndianTaxOptimizer()
    
    # Analyze portfolio
    print("=== Tax Analysis ===")
    portfolio_analysis = await tax_optimizer.analyze_portfolio_tax_implications(sample_holdings)
    
    print(f"Total Unrealized Gains: ₹{portfolio_analysis['unrealized_analysis']['unrealized_gains']:,.2f}")
    print(f"Total Unrealized Losses: ₹{portfolio_analysis['unrealized_analysis']['unrealized_losses']:,.2f}")
    print(f"Tax Liability if sold today: ₹{portfolio_analysis['unrealized_analysis']['potential_tax_if_sold_today']:,.2f}")
    
    # Generate optimization strategies
    print("\n=== Tax Optimization Strategies ===")
    strategies = await tax_optimizer.generate_tax_optimization_strategies(
        portfolio_analysis, available_cash=200000
    )
    
    for i, strategy in enumerate(strategies, 1):
        print(f"\n{i}. {strategy.strategy_name}")
        print(f"   Potential Saving: ₹{strategy.potential_tax_saving:,.2f}")
        print(f"   Risk Level: {strategy.risk_level}")
        print(f"   Timeline: {strategy.timeline}")
        print(f"   Description: {strategy.description}")
    
    # Tax harvesting opportunities
    print("\n=== Tax Harvesting Opportunities ===")
    harvesting_opportunities = await tax_optimizer.identify_tax_harvesting_opportunities(
        portfolio_analysis['holdings_analysis']
    )
    
    for opp in harvesting_opportunities:
        print(f"Sell {opp.sell_symbol}: Save ₹{opp.net_tax_benefit:,.2f} in taxes")
    
    # Holding period calendar
    print("\n=== LTCG Eligibility Calendar ===")
    ltcg_calendar = tax_optimizer.calculate_holding_period_calendar(sample_holdings)
    print(f"Positions becoming LTCG eligible: {ltcg_calendar['total_positions_becoming_ltcg']}")
    print(f"Potential tax saving: ₹{ltcg_calendar['total_potential_tax_saving']:,.2f}")
    
    # Year-end checklist
    print("\n=== Year-End Tax Checklist ===")
    checklist = tax_optimizer.generate_year_end_tax_checklist()
    for category, items in checklist.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")
    
    # Export report
    report = tax_optimizer.export_tax_report(portfolio_analysis, strategies)
    print(f"\nTax report generated: {len(report)} characters")


if __name__ == "__main__":
    asyncio.run(test_tax_optimizer())