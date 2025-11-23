"""
Unit tests for data models
Run with: python -m pytest tests/test_models.py
"""
import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.models_improved import Stock, PortfolioSummary, StockValidationError


class TestStockModel:
    """Test cases for Stock dataclass"""

    def test_valid_stock_creation(self):
        """Test creating a valid stock"""
        stock = Stock(
            symbol="RELIANCE.NS",
            company_name="Reliance Industries Limited",
            quantity=100,
            purchase_price=2200,
            purchase_date="2023-06-15"
        )

        assert stock.symbol == "RELIANCE.NS"
        assert stock.quantity == 100
        assert stock.purchase_price == 2200
        assert stock.total_investment == 220000

    def test_stock_symbol_normalization(self):
        """Test that symbols are normalized to uppercase"""
        stock = Stock(
            symbol="  reliance.ns  ",
            company_name="Reliance",
            quantity=100,
            purchase_price=2200,
            purchase_date="2023-06-15"
        )

        assert stock.symbol == "RELIANCE.NS"

    def test_invalid_quantity(self):
        """Test that invalid quantities raise errors"""
        with pytest.raises(StockValidationError, match="Quantity must be at least"):
            Stock(
                symbol="RELIANCE.NS",
                company_name="Reliance",
                quantity=0,  # Invalid
                purchase_price=2200,
                purchase_date="2023-06-15"
            )

        with pytest.raises(StockValidationError, match="Quantity must be at least"):
            Stock(
                symbol="RELIANCE.NS",
                company_name="Reliance",
                quantity=-10,  # Invalid
                purchase_price=2200,
                purchase_date="2023-06-15"
            )

    def test_invalid_purchase_price(self):
        """Test that invalid prices raise errors"""
        with pytest.raises(StockValidationError, match="Purchase price must be at least"):
            Stock(
                symbol="RELIANCE.NS",
                company_name="Reliance",
                quantity=100,
                purchase_price=0,  # Invalid
                purchase_date="2023-06-15"
            )

    def test_invalid_date_format(self):
        """Test that invalid date formats raise errors"""
        with pytest.raises(StockValidationError, match="Invalid date format"):
            Stock(
                symbol="RELIANCE.NS",
                company_name="Reliance",
                quantity=100,
                purchase_price=2200,
                purchase_date="15-06-2023"  # Wrong format
            )

    def test_future_date_rejected(self):
        """Test that future dates are rejected"""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        with pytest.raises(StockValidationError, match="cannot be in the future"):
            Stock(
                symbol="RELIANCE.NS",
                company_name="Reliance",
                quantity=100,
                purchase_price=2200,
                purchase_date=future_date
            )

    def test_cash_invested_auto_calculation(self):
        """Test that cash_invested is auto-calculated"""
        stock = Stock(
            symbol="RELIANCE.NS",
            company_name="Reliance",
            quantity=100,
            purchase_price=2200,
            purchase_date="2023-06-15"
        )

        assert stock.cash_invested == 220000

    def test_profit_loss_calculation(self):
        """Test profit/loss calculations"""
        stock = Stock(
            symbol="RELIANCE.NS",
            company_name="Reliance",
            quantity=100,
            purchase_price=2200,
            purchase_date="2023-06-15",
            current_price=2500
        )

        assert stock.current_value == 250000
        assert stock.profit_loss_amount == 30000
        assert abs(stock.profit_loss_percentage - 13.64) < 0.01

    def test_days_held_calculation(self):
        """Test days held calculation"""
        # Stock purchased 365 days ago
        past_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        stock = Stock(
            symbol="RELIANCE.NS",
            company_name="Reliance",
            quantity=100,
            purchase_price=2200,
            purchase_date=past_date
        )

        assert 364 <= stock.days_held <= 366  # Allow for slight variations

    def test_annualized_return(self):
        """Test annualized return calculation"""
        past_date = (datetime.now() - timedelta(days=182)).strftime("%Y-%m-%d")  # 6 months

        stock = Stock(
            symbol="RELIANCE.NS",
            company_name="Reliance",
            quantity=100,
            purchase_price=2000,
            purchase_date=past_date,
            current_price=2200
        )

        # 10% return over 6 months ≈ 20% annualized
        assert 18 <= stock.annualized_return <= 22

    def test_is_profitable_property(self):
        """Test is_profitable property"""
        profitable_stock = Stock(
            symbol="RELIANCE.NS",
            company_name="Reliance",
            quantity=100,
            purchase_price=2000,
            purchase_date="2023-06-15",
            current_price=2500
        )

        loss_stock = Stock(
            symbol="TCS.NS",
            company_name="TCS",
            quantity=100,
            purchase_price=3500,
            purchase_date="2023-06-15",
            current_price=3000
        )

        assert profitable_stock.is_profitable is True
        assert loss_stock.is_profitable is False


class TestPortfolioSummary:
    """Test cases for PortfolioSummary"""

    def test_portfolio_summary_creation(self):
        """Test creating a portfolio summary"""
        summary = PortfolioSummary(
            total_investment=500000,
            current_value=550000,
            total_profit_loss=50000,
            total_profit_loss_percentage=10.0,
            total_stocks=5
        )

        assert summary.total_investment == 500000
        assert summary.current_value == 550000
        assert summary.total_profit_loss == 50000
        assert summary.is_profitable is True

    def test_portfolio_negative_values(self):
        """Test portfolio with loss"""
        summary = PortfolioSummary(
            total_investment=500000,
            current_value=450000,
            total_profit_loss=-50000,
            total_profit_loss_percentage=-10.0,
            total_stocks=5
        )

        assert summary.is_profitable is False

    def test_average_return_calculation(self):
        """Test average return per stock"""
        summary = PortfolioSummary(
            total_investment=500000,
            current_value=550000,
            total_profit_loss=50000,
            total_profit_loss_percentage=10.0,
            total_stocks=5
        )

        assert summary.average_return == 2.0  # 10% / 5 stocks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
