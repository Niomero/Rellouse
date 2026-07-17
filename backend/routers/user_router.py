"""
User Router
Handles user-related endpoints: search, profile, status
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from database import get_db
from models import User, UserRole
from auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


# Pydantic models
class UserSearchResponse(BaseModel):
    id: int
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    role: str
    is_verified: bool
    is_online: bool
    is_bot: bool

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: int
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    role: str
    is_verified: bool
    is_online: bool
    is_bot: bool
    last_seen: Optional[datetime]
    created_at: datetime
    additional_usernames: Optional[List[str]]

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


@router.get("/search", response_model=List[UserSearchResponse])
async def search_users(
    query: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search users by login, username, or display name
    Supports partial matching and @username format
    """
    # Remove @ if present
    search_query = query.strip()
    if search_query.startswith("@"):
        search_query = search_query[1:]
    
    # Build search query
    search_pattern = f"%{search_query}%"
    
    stmt = select(User).where(
        User.is_active == True,
        or_(
            User.login.ilike(search_pattern),
            User.username.ilike(search_pattern),
            User.display_name.ilike(search_pattern),
            User.username.ilike(f"%@{search_query}%")
        )
    ).limit(limit)
    
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    # Convert to response format
    response = []
    for user in users:
        response.append(UserSearchResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            role=user.role.value,
            is_verified=user.role in [UserRole.VERIFIED, UserRole.ADMINISTRATOR, UserRole.OWNER],
            is_online=user.is_online,
            is_bot=user.is_bot
        ))
    
    return response


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed user profile by ID
    """
    stmt = select(User).where(User.id == user_id, User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Parse additional usernames
    additional_usernames = None
    if user.additional_usernames:
        try:
            additional_usernames = json.loads(user.additional_usernames)
        except:
            additional_usernames = []
    
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        bio=user.bio,
        role=user.role.value,
        is_verified=user.role in [UserRole.VERIFIED, UserRole.ADMINISTRATOR, UserRole.OWNER],
        is_online=user.is_online,
        is_bot=user.is_bot,
        last_seen=user.last_seen,
        created_at=user.created_at,
        additional_usernames=additional_usernames
    )


@router.get("/username/{username}", response_model=UserProfileResponse)
async def get_user_by_username(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user profile by username (@username)
    """
    # Remove @ if present
    if username.startswith("@"):
        username = username[1:]
    
    stmt = select(User).where(
        User.username == f"@{username}",
        User.is_active == True
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Parse additional usernames
    additional_usernames = None
    if user.additional_usernames:
        try:
            additional_usernames = json.loads(user.additional_usernames)
        except:
            additional_usernames = []
    
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        bio=user.bio,
        role=user.role.value,
        is_verified=user.role in [UserRole.VERIFIED, UserRole.ADMINISTRATOR, UserRole.OWNER],
        is_online=user.is_online,
        is_bot=user.is_bot,
        last_seen=user.last_seen,
        created_at=user.created_at,
        additional_usernames=additional_usernames
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    update_data: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile
    """
    if update_data.display_name is not None:
        current_user.display_name = update_data.display_name
    
    if update_data.bio is not None:
        current_user.bio = update_data.bio
    
    if update_data.avatar_url is not None:
        current_user.avatar_url = update_data.avatar_url
    
    current_user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(current_user)
    
    # Parse additional usernames
    additional_usernames = None
    if current_user.additional_usernames:
        try:
            additional_usernames = json.loads(current_user.additional_usernames)
        except:
            additional_usernames = []
    
    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        role=current_user.role.value,
        is_verified=current_user.role in [UserRole.VERIFIED, UserRole.ADMINISTRATOR, UserRole.OWNER],
        is_online=current_user.is_online,
        is_bot=current_user.is_bot,
        last_seen=current_user.last_seen,
        created_at=current_user.created_at,
        additional_usernames=additional_usernames
    )


@router.get("/online/list", response_model=List[int])
async def get_online_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of online user IDs
    """
    stmt = select(User.id).where(User.is_online == True, User.is_active == True)
    result = await db.execute(stmt)
    user_ids = result.scalars().all()
    
    return list(user_ids)