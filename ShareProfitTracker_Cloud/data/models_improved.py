"""
Improved Data Models with validation and better error handling
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

try:
    from utils.logger import get_logger
    from config.constants import MIN_QUANTITY, MIN_PRICE, MAX_QUANTITY, MAX_PRICE, DATE_FORMAT
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)
    MIN_QUANTITY = 0.0001
    MIN_PRICE = 0.01
    MAX_QUANTITY = 1000000000
    MAX_PRICE = 10000000
    DATE_FORMAT = "%Y-%m-%d"

logger = get_logger(__name__)


class StockValidationError(Exception):
    """Exception raised for stock validation errors"""
    pass


@dataclass
class Stock:
    """
    Stock data model with validation

    Attributes:
        symbol: Stock ticker symbol
        company_name: Company name
        quantity: Number of shares
        purchase_price: Price per share at purchase
        purchase_date: Purchase date (YYYY-MM-DD)
        broker: Broker name (optional)
        cash_invested: Actual cash invested (optional, auto-calculated)
        id: Database ID (optional)
        user_id: User ID (optional)
        current_price: Current market price (optional)
        last_updated: Last price update timestamp (optional)
        created_at: Record creation timestamp (optional)
        sector: Stock sector/industry (optional)
        dividend_yield: Annual dividend yield percentage (optional)
        beta: Stock beta coefficient for volatility (optional)
    """
    symbol: str
    company_name: str
    quantity: float
    purchase_price: float
    purchase_date: str
    broker: str = ""
    cash_invested: float = 0
    id: Optional[int] = None
    user_id: Optional[int] = None
    current_price: Optional[float] = None
    last_updated: Optional[str] = None
    created_at: Optional[str] = None
    sector: Optional[str] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None

    def __post_init__(self):
        """
        Validate stock data after initialization

        Raises:
            StockValidationError: If validation fails
        """
        # Validate and normalize symbol
        if not self.symbol or not isinstance(self.symbol, str):
            raise StockValidationError("Symbol must be a non-empty string")

        self.symbol = self.symbol.upper().strip()

        if not self.symbol:
            raise StockValidationError("Symbol cannot be empty after trimming")

        # Validate company name
        if not self.company_name or not isinstance(self.company_name, str):
            raise StockValidationError("Company name must be a non-empty string")

        self.company_name = self.company_name.strip()

        # Validate quantity
        if not isinstance(self.quantity, (int, float)):
            raise StockValidationError(f"Quantity must be a number, got {type(self.quantity).__name__}")

        if self.quantity < MIN_QUANTITY:
            raise StockValidationError(
                f"Quantity must be at least {MIN_QUANTITY}, got {self.quantity}"
            )

        if self.quantity > MAX_QUANTITY:
            raise StockValidationError(
                f"Quantity cannot exceed {MAX_QUANTITY:,.0f}, got {self.quantity:,.0f}"
            )

        # Validate purchase price
        if not isinstance(self.purchase_price, (int, float)):
            raise StockValidationError(
                f"Purchase price must be a number, got {type(self.purchase_price).__name__}"
            )

        if self.purchase_price < MIN_PRICE:
            raise StockValidationError(
                f"Purchase price must be at least ₹{MIN_PRICE}, got ₹{self.purchase_price}"
            )

        if self.purchase_price > MAX_PRICE:
            raise StockValidationError(
                f"Purchase price cannot exceed ₹{MAX_PRICE:,.0f}, got ₹{self.purchase_price:,.0f}"
            )

        # Validate date format and value
        try:
            date_obj = datetime.strptime(self.purchase_date, DATE_FORMAT)

            # Check if date is in the future
            if date_obj > datetime.now():
                raise StockValidationError(
                    f"Purchase date cannot be in the future: {self.purchase_date}"
                )

            # Check if date is reasonable (not before 1900)
            if date_obj.year < 1900:
                raise StockValidationError(
                    f"Purchase date seems invalid: {self.purchase_date}"
                )

        except ValueError as e:
            raise StockValidationError(
                f"Invalid date format '{self.purchase_date}'. Use YYYY-MM-DD format"
            ) from e

        # Auto-calculate cash_invested if not provided
        if self.cash_invested == 0:
            self.cash_invested = self.quantity * self.purchase_price
            logger.debug(
                f"Auto-calculated cash_invested for {self.symbol}: "
                f"₹{self.cash_invested:,.2f}"
            )

        # Validate cash_invested is reasonable
        if self.cash_invested < 0:
            raise StockValidationError(
                f"Cash invested cannot be negative: ₹{self.cash_invested}"
            )

    @property
    def total_investment(self) -> float:
        """
        Calculate total investment based on quantity and purchase price

        Returns:
            Total investment amount
        """
        return self.quantity * self.purchase_price

    @property
    def actual_cash_invested(self) -> float:
        """
        Returns the actual cash invested (different from calculated investment)

        This may include brokerage fees, taxes, etc.

        Returns:
            Actual cash invested amount
        """
        return self.cash_invested

    @property
    def current_value(self) -> float:
        """
        Calculate current value of holding

        Returns:
            Current value (0 if price not available)
        """
        if self.current_price is None:
            return 0.0
        return self.quantity * self.current_price

    @property
    def profit_loss_amount(self) -> float:
        """
        Calculate profit/loss amount

        Returns:
            Profit (positive) or loss (negative) amount
        """
        return self.current_value - self.total_investment

    @property
    def profit_loss_percentage(self) -> float:
        """
        Calculate profit/loss percentage

        Returns:
            Profit/loss percentage (0 if no investment)
        """
        if self.total_investment == 0:
            logger.warning(f"Total investment is 0 for {self.symbol}")
            return 0.0
        return (self.profit_loss_amount / self.total_investment) * 100

    @property
    def days_held(self) -> int:
        """
        Calculate number of days stock has been held

        Returns:
            Number of days (0 if date parsing fails)
        """
        try:
            purchase_dt = datetime.strptime(self.purchase_date, DATE_FORMAT)
            days = (datetime.now() - purchase_dt).days
            return max(0, days)  # Ensure non-negative
        except ValueError as e:
            logger.error(f"Error parsing purchase date for {self.symbol}: {e}")
            return 0

    @property
    def annualized_return(self) -> float:
        """
        Calculate annualized return percentage

        Returns:
            Annualized return percentage (0 if held < 1 day)
        """
        days = self.days_held
        if days == 0:
            return 0.0

        # Annualize the return
        return (self.profit_loss_percentage / days) * 365

    @property
    def is_profitable(self) -> bool:
        """Check if stock is currently profitable"""
        return self.profit_loss_amount > 0

    @property
    def price_change_percentage(self) -> Optional[float]:
        """
        Calculate percentage change from purchase price to current price

        Returns:
            Percentage change, or None if current price unavailable
        """
        if self.current_price is None:
            return None
        if self.purchase_price == 0:
            return None
        return ((self.current_price - self.purchase_price) / self.purchase_price) * 100

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"Stock(symbol='{self.symbol}', company='{self.company_name}', "
            f"qty={self.quantity}, price=₹{self.purchase_price:.2f}, "
            f"value=₹{self.current_value:,.2f}, P/L={self.profit_loss_percentage:+.2f}%)"
        )


@dataclass
class PortfolioSummary:
    """
    Portfolio summary statistics

    Attributes:
        total_investment: Total amount invested
        current_value: Current total portfolio value
        total_profit_loss: Total profit/loss amount
        total_profit_loss_percentage: Total profit/loss percentage
        best_performer: Stock with highest gain percentage (optional)
        worst_performer: Stock with lowest gain percentage (optional)
        total_stocks: Number of stocks in portfolio
    """
    total_investment: float
    current_value: float
    total_profit_loss: float
    total_profit_loss_percentage: float
    best_performer: Optional[Stock] = None
    worst_performer: Optional[Stock] = None
    total_stocks: int = 0

    def __post_init__(self):
        """Validate summary data"""
        if self.total_investment < 0:
            logger.warning(f"Negative total investment: ₹{self.total_investment}")

        if self.current_value < 0:
            logger.warning(f"Negative current value: ₹{self.current_value}")

        if self.total_stocks < 0:
            raise ValueError("Total stocks cannot be negative")

    @property
    def is_profitable(self) -> bool:
        """Check if overall portfolio is profitable"""
        return self.total_profit_loss > 0

    @property
    def average_return(self) -> float:
        """Calculate average return per stock"""
        if self.total_stocks == 0:
            return 0.0
        return self.total_profit_loss_percentage / self.total_stocks

    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"PortfolioSummary(stocks={self.total_stocks}, "
            f"invested=₹{self.total_investment:,.2f}, "
            f"value=₹{self.current_value:,.2f}, "
            f"P/L={self.total_profit_loss_percentage:+.2f}%)"
        )
