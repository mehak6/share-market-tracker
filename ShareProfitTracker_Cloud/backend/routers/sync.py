"""
Sync router - handles data synchronization between desktop and cloud
"""

from fastapi import APIRouter, HTTPException, Header
from datetime import datetime
from ..models import SyncData, SyncResponse
from ..database import get_supabase_client

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

@router.post("/upload", response_model=SyncResponse)
async def upload_data(data: SyncData, authorization: str = Header(...)):
    """
    Upload local data to cloud (full sync from desktop).
    This replaces all cloud data with local data.
    """
    user_id = get_user_id(authorization)
    supabase = get_supabase_client()

    try:
        # Clear existing data
        supabase.table("stocks").delete().eq("user_id", user_id).execute()
        supabase.table("cash_transactions").delete().eq("user_id", user_id).execute()
        supabase.table("expenses").delete().eq("user_id", user_id).execute()
        supabase.table("dividends").delete().eq("user_id", user_id).execute()

        # Upload stocks
        if data.stocks:
            stocks_data = [{**s, "user_id": user_id} for s in data.stocks]
            supabase.table("stocks").insert(stocks_data).execute()

        # Upload cash transactions
        if data.cash_transactions:
            cash_data = [{**c, "user_id": user_id} for c in data.cash_transactions]
            supabase.table("cash_transactions").insert(cash_data).execute()

        # Upload expenses
        if data.expenses:
            expenses_data = [{**e, "user_id": user_id} for e in data.expenses]
            supabase.table("expenses").insert(expenses_data).execute()

        # Upload dividends
        if data.dividends:
            dividends_data = [{**d, "user_id": user_id} for d in data.dividends]
            supabase.table("dividends").insert(dividends_data).execute()

        return SyncResponse(
            success=True,
            message=f"Uploaded {len(data.stocks)} stocks, {len(data.cash_transactions)} transactions, {len(data.expenses)} expenses, {len(data.dividends)} dividends",
            last_sync=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/download", response_model=SyncResponse)
async def download_data(authorization: str = Header(...)):
    """
    Download cloud data to local (full sync to desktop).
    Returns all user data from cloud.
    """
    user_id = get_user_id(authorization)
    supabase = get_supabase_client()

    try:
        # Get all data
        stocks = supabase.table("stocks").select("*").eq("user_id", user_id).execute()
        cash = supabase.table("cash_transactions").select("*").eq("user_id", user_id).execute()
        expenses = supabase.table("expenses").select("*").eq("user_id", user_id).execute()
        dividends = supabase.table("dividends").select("*").eq("user_id", user_id).execute()

        sync_data = SyncData(
            stocks=stocks.data,
            cash_transactions=cash.data,
            expenses=expenses.data,
            dividends=dividends.data
        )

        return SyncResponse(
            success=True,
            message=f"Downloaded {len(stocks.data)} stocks, {len(cash.data)} transactions, {len(expenses.data)} expenses, {len(dividends.data)} dividends",
            data=sync_data,
            last_sync=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.get("/status")
async def sync_status(authorization: str = Header(...)):
    """Get sync status and counts"""
    user_id = get_user_id(authorization)
    supabase = get_supabase_client()

    try:
        stocks = supabase.table("stocks").select("id", count="exact").eq("user_id", user_id).execute()
        cash = supabase.table("cash_transactions").select("id", count="exact").eq("user_id", user_id).execute()
        expenses = supabase.table("expenses").select("id", count="exact").eq("user_id", user_id).execute()
        dividends = supabase.table("dividends").select("id", count="exact").eq("user_id", user_id).execute()

        return {
            "stocks_count": stocks.count or 0,
            "cash_transactions_count": cash.count or 0,
            "expenses_count": expenses.count or 0,
            "dividends_count": dividends.count or 0,
            "last_checked": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
