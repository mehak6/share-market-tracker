"""
Stocks router - CRUD operations for stocks
"""

from fastapi import APIRouter, HTTPException, status, Header
from typing import List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import StockCreate, StockUpdate, StockResponse
from database import get_supabase_client

router = APIRouter()

def get_user_id(authorization: str) -> str:
    """Extract user ID from authorization token"""
    try:
        token = authorization.replace("Bearer ", "")
        supabase = get_supabase_client()
        response = supabase.auth.get_user(token)
        if response.user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return response.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/", response_model=List[StockResponse])
async def get_stocks(authorization: str = Header(...)):
    """Get all stocks for current user"""
    user_id = get_user_id(authorization)
    supabase = get_supabase_client()

    response = supabase.table("stocks").select("*").eq("user_id", user_id).execute()
    return response.data

@router.post("/", response_model=StockResponse)
async def create_stock(stock: StockCreate, authorization: str = Header(...)):
    """Create a new stock"""
    user_id = get_user_id(authorization)
    supabase = get_supabase_client()

    # Calculate cash_invested if not provided
    cash_invested = stock.cash_invested
    if cash_invested == 0:
        cash_invested = stock.quantity * stock.purchase_price

    data = {
        "user_id": user_id,
        "symbol": stock.symbol.upper(),
        "company_name": stock.company_name,
        "quantity": stock.quantity,
        "purchase_price": stock.purchase_price,
        "purchase_date": stock.purchase_date,
        "broker": stock.broker,
        "cash_invested": cash_invested
    }

    response = supabase.table("stocks").insert(data).execute()

    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create stock")

    return response.data[0]

@router.put("/{stock_id}", response_model=StockResponse)
async def update_stock(stock_id: str, stock: StockUpdate, authorization: str = Header(...)):
    """Update a stock"""
    user_id = get_user_id(authorization)
    supabase = get_supabase_client()

    # Build update data (only non-None fields)
    update_data = {}
    for field, value in stock.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value

    if "symbol" in update_data:
        update_data["symbol"] = update_data["symbol"].upper()

    response = supabase.table("stocks").update(update_data).eq("id", stock_id).eq("user_id", user_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Stock not found")

    return response.data[0]

@router.delete("/{stock_id}")
async def delete_stock(stock_id: str, authorization: str = Header(...)):
    """Delete a stock"""
    user_id = get_user_id(authorization)
    supabase = get_supabase_client()

    response = supabase.table("stocks").delete().eq("id", stock_id).eq("user_id", user_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Stock not found")

    return {"message": "Stock deleted successfully"}
