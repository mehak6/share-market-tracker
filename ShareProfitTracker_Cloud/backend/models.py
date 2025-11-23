"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Auth models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    display_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    display_name: str

class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    created_at: datetime

# Stock models
class StockCreate(BaseModel):
    symbol: str
    company_name: str
    quantity: float
    purchase_price: float
    purchase_date: str
    broker: Optional[str] = ""
    cash_invested: Optional[float] = 0

class StockUpdate(BaseModel):
    symbol: Optional[str] = None
    company_name: Optional[str] = None
    quantity: Optional[float] = None
    purchase_price: Optional[float] = None
    purchase_date: Optional[str] = None
    broker: Optional[str] = None
    cash_invested: Optional[float] = None

class StockResponse(BaseModel):
    id: str
    user_id: str
    symbol: str
    company_name: str
    quantity: float
    purchase_price: float
    purchase_date: str
    broker: str
    cash_invested: float
    created_at: datetime

# Cash transaction models
class CashTransactionCreate(BaseModel):
    transaction_type: str  # 'deposit' or 'withdrawal'
    amount: float
    description: Optional[str] = ""
    transaction_date: str

class CashTransactionResponse(BaseModel):
    id: str
    user_id: str
    transaction_type: str
    amount: float
    description: str
    transaction_date: str
    created_at: datetime

# Expense models
class ExpenseCreate(BaseModel):
    category: str
    description: str
    amount: float
    expense_date: str

class ExpenseResponse(BaseModel):
    id: str
    user_id: str
    category: str
    description: str
    amount: float
    expense_date: str
    created_at: datetime

# Dividend models
class DividendCreate(BaseModel):
    symbol: str
    company_name: str
    dividend_per_share: float
    total_dividend: float
    shares_held: float
    ex_dividend_date: str
    payment_date: Optional[str] = None
    dividend_type: Optional[str] = "regular"
    tax_deducted: Optional[float] = 0

class DividendResponse(BaseModel):
    id: str
    user_id: str
    symbol: str
    company_name: str
    dividend_per_share: float
    total_dividend: float
    shares_held: float
    ex_dividend_date: str
    payment_date: Optional[str]
    dividend_type: str
    tax_deducted: float
    net_dividend: float
    created_at: datetime

# Sync models
class SyncData(BaseModel):
    stocks: List[dict]
    cash_transactions: List[dict]
    expenses: List[dict]
    dividends: List[dict]
    last_sync: Optional[str] = None

class SyncResponse(BaseModel):
    success: bool
    message: str
    data: Optional[SyncData] = None
    last_sync: str
