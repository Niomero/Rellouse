"""
Authentication Router
Handles user registration, login, logout, and token refresh
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional
from database import get_db
from auth import auth_service
from models import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class RegisterRequest(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=5, max_length=17, pattern=r"^@[a-zA-Z0-9_]{4,16}$")


class LoginRequest(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    success: bool
    message: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    
    - **login**: Unique login (3-50 characters)
    - **password**: Password (minimum 8 characters)
    - **username**: Username starting with @ (4-16 characters after @)
    """
    ip_address = http_request.client.host
    user_agent = http_request.headers.get("user-agent")
    
    # Register user
    result = await auth_service.register_user(
        db=db,
        login=request.login,
        password=request.password,
        username=request.username,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    user = result["user"]
    
    # Auto-login after registration
    login_result = await auth_service.login_user(
        db=db,
        login=request.login,
        password=request.password,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not login_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration successful but auto-login failed"
        )
    
    return TokenResponse(
        access_token=login_result["access_token"],
        refresh_token=login_result["refresh_token"],
        user={
            "id": user.id,
            "username": user.username,
            "role": user.role.value
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with credentials
    
    - **login**: User login
    - **password**: User password
    """
    ip_address = http_request.client.host
    user_agent = http_request.headers.get("user-agent")
    
    result = await auth_service.login_user(
        db=db,
        login=request.login,
        password=request.password,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"]
        )
    
    user = result["user"]
    
    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        user={
            "id": user.id,
            "username": user.username,
            "role": user.role.value
        }
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    """
    result = await auth_service.refresh_access_token(
        db=db,
        refresh_token=request.refresh_token
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"]
        )
    
    return {
        "access_token": result["access_token"],
        "token_type": "bearer"
    }


@router.post("/logout", response_model=MessageResponse)
async def logout(
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Logout and invalidate session
    
    Requires: Bearer token in Authorization header
    """
    # Extract token from Authorization header
    auth_header = http_request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    access_token = auth_header.split(" ")[1]
    
    result = await auth_service.logout_user(
        db=db,
        access_token=access_token
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Logout failed")
        )
    
    return MessageResponse(
        success=True,
        message="Logged out successfully"
    )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information
    
    Requires: Bearer token in Authorization header
    """
    # Extract token from Authorization header
    auth_header = http_request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    access_token = auth_header.split(" ")[1]
    
    user = await auth_service.get_current_user(
        db=db,
        access_token=access_token
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Parse additional usernames
    import json
    additional_usernames = []
    if user.additional_usernames:
        try:
            additional_usernames = json.loads(user.additional_usernames)
        except:
            pass
    
    return {
        "id": user.id,
        "username": user.username,
        "additional_usernames": additional_usernames,
        "role": user.role.value,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None
    }
