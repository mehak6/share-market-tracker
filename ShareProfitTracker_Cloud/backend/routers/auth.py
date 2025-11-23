"""
Authentication router - handles user registration and login
"""

from fastapi import APIRouter, HTTPException, status
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import UserCreate, UserLogin, Token, UserResponse
from database import get_supabase_client

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    """Register a new user"""
    try:
        supabase = get_supabase_client()

        # Create user with Supabase Auth
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "display_name": user.display_name
                }
            }
        })

        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. Please try again."
            )

        # Create user profile
        supabase.table("user_profiles").insert({
            "id": response.user.id,
            "display_name": user.display_name
        }).execute()

        return Token(
            access_token=response.session.access_token,
            user_id=response.user.id,
            display_name=user.display_name
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login user and return access token"""
    try:
        supabase = get_supabase_client()

        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })

        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Get display name from user metadata or profile
        display_name = response.user.user_metadata.get("display_name", user.email)

        return Token(
            access_token=response.session.access_token,
            user_id=response.user.id,
            display_name=display_name
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

@router.post("/logout")
async def logout():
    """Logout user (client should discard token)"""
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str):
    """Get current user info"""
    try:
        supabase = get_supabase_client()

        # Verify token and get user
        response = supabase.auth.get_user(token)

        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        return UserResponse(
            id=response.user.id,
            email=response.user.email,
            display_name=response.user.user_metadata.get("display_name", response.user.email),
            created_at=response.user.created_at
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
