"""
Unit tests for portfolio calculator
Run with: python -m pytest tests/test_calculator.py
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.calculator import PortfolioCalculator
from data.models_improved import Stock


class TestPortfolioCalculator:
    """Test cases for PortfolioCalculator"""

    def test_empty_portfolio(self):
        """Test calculator with empty portfolio"""
        calculator = PortfolioCalculator()
        summary = calculator.calculate_portfolio_summary([])

        assert summary.total_investment == 0
        assert summary.current_value == 0
        assert summary.total_profit_loss == 0
        assert summary.total_stocks == 0

    def test_single_stock_profitable(self):
        """Test calculator with single profitable stock"""
        stock = Stock(
            symbol="RELIANCE.NS",
            company_name="Reliance",
            quantity=100,
            purchase_price=2000,
            purchase_date="2023-06-15",
            current_price=2500
        )

        calculator = PortfolioCalculator()
        summary = calculator.calculate_portfolio_summary([stock])

        assert summary.total_investment == 200000
        assert summary.current_value == 250000
        assert summary.total_profit_loss == 50000
        assert summary.total_profit_loss_percentage == 25.0
        assert summary.total_stocks == 1

    def test_multiple_stocks_mixed(self):
        """Test calculator with multiple stocks (mix of profit/loss)"""
        stocks = [
            Stock(
                symbol="RELIANCE.NS",
                company_name="Reliance",
                quantity=100,
                purchase_price=2000,
                purchase_date="2023-06-15",
                current_price=2500  # +25%
            ),
            Stock(
                symbol="TCS.NS",
                company_name="TCS",
                quantity=50,
                purchase_price=3000,
                purchase_date="2023-06-15",
                current_price=2700  # -10%
            ),
        ]

        calculator = PortfolioCalculator()
        summary = calculator.calculate_portfolio_summary(stocks)

        # Total investment: 200000 + 150000 = 350000
        # Current value: 250000 + 135000 = 385000
        # Profit: 35000
        assert summary.total_investment == 350000
        assert summary.current_value == 385000
        assert summary.total_profit_loss == 35000
        assert summary.total_stocks == 2

    def test_best_worst_performers(self):
        """Test identification of best and worst performers"""
        stocks = [
            Stock(
                symbol="WINNER.NS",
                company_name="Winner Corp",
                quantity=100,
                purchase_price=1000,
                purchase_date="2023-06-15",
                current_price=1500  # +50%
            ),
            Stock(
                symbol="MIDDLE.NS",
                company_name="Middle Corp",
                quantity=100,
                purchase_price=2000,
                purchase_date="2023-06-15",
                current_price=2100  # +5%
            ),
            Stock(
                symbol="LOSER.NS",
                company_name="Loser Corp",
                quantity=100,
                purchase_price=3000,
                purchase_date="2023-06-15",
                current_price=2400  # -20%
            ),
        ]

        calculator = PortfolioCalculator()
        summary = calculator.calculate_portfolio_summary(stocks)

        assert summary.best_performer.symbol == "WINNER.NS"
        assert summary.worst_performer.symbol == "LOSER.NS"

    def test_stock_without_current_price(self):
        """Test handling of stocks without current price"""
        stocks = [
            Stock(
                symbol="PRICED.NS",
                company_name="Has Price",
                quantity=100,
                purchase_price=2000,
                purchase_date="2023-06-15",
                current_price=2500
            ),
            Stock(
                symbol="NOPRICE.NS",
                company_name="No Price",
                quantity=100,
                purchase_price=1000,
                purchase_date="2023-06-15",
                current_price=None  # No price
            ),
        ]

        calculator = PortfolioCalculator()
        summary = calculator.calculate_portfolio_summary(stocks)

        # Should only include stocks with prices in current_value
        assert summary.total_investment == 300000  # Both stocks
        assert summary.current_value == 250000  # Only first stock
        assert summary.total_stocks == 2

    def test_format_currency(self):
        """Test currency formatting"""
        formatted = PortfolioCalculator.format_currency(1234567.89)
        assert "₹" in formatted
        assert "1,234,567.89" in formatted

    def test_format_percentage(self):
        """Test percentage formatting"""
        positive = PortfolioCalculator.format_percentage(15.5)
        negative = PortfolioCalculator.format_percentage(-10.2)

        assert "+" in positive
        assert "15.50%" in positive
        assert "-10.20%" in negative

    def test_profit_loss_color(self):
        """Test color determination for profit/loss"""
        assert PortfolioCalculator.get_profit_loss_color(100) == "green"
        assert PortfolioCalculator.get_profit_loss_color(-100) == "red"
        assert PortfolioCalculator.get_profit_loss_color(0) == "black"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
