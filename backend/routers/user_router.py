"""
User Router
Handles user profile operations, search, and management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List
from database import get_db
from auth import auth_service
from user_service import user_service
from models import UserRole
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Dependency to get current user
async def get_current_user(
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Dependency to extract and validate current user from token"""
    auth_header = http_request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    access_token = auth_header.split(" ")[1]
    user = await auth_service.get_current_user(db=db, access_token=access_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user


# Request/Response Models
class UpdateProfileRequest(BaseModel):
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None


class UpdateUsernameRequest(BaseModel):
    new_username: str = Field(..., min_length=5, max_length=17, pattern=r"^@[a-zA-Z0-9_]{4,16}$")


class AddAdditionalUsernameRequest(BaseModel):
    username: str = Field(..., min_length=5, max_length=17, pattern=r"^@[a-zA-Z0-9_]{4,16}$")


class UpdateRoleRequest(BaseModel):
    user_id: int
    new_role: str = Field(..., pattern=r"^(user|verified|administrator|owner)$")


@router.get("/search")
async def search_users(
    q: str,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Search users by username
    
    - **q**: Search query (username)
    - **limit**: Maximum results (default: 20)
    - **offset**: Pagination offset (default: 0)
    """
    users = await user_service.search_users(
        db=db,
        query=q,
        limit=limit,
        offset=offset
    )
    
    import json
    result = []
    for user in users:
        additional_usernames = []
        if user.additional_usernames:
            try:
                additional_usernames = json.loads(user.additional_usernames)
            except:
                pass
        
        result.append({
            "id": user.id if current_user.role in [UserRole.OWNER, UserRole.ADMINISTRATOR] else None,
            "username": user.username,
            "additional_usernames": additional_usernames if user.role in [UserRole.OWNER, UserRole.ADMINISTRATOR] else [],
            "role": user.role.value,
            "avatar_url": user.avatar_url,
            "bio": user.bio
        })
    
    return {"users": result, "count": len(result)}


@router.get("/{username}")
async def get_user_profile(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get user profile by username
    
    - **username**: Username (with or without @)
    """
    user = await user_service.get_user_by_username(db=db, username=username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    import json
    additional_usernames = []
    if user.additional_usernames:
        try:
            additional_usernames = json.loads(user.additional_usernames)
        except:
            pass
    
    return {
        "id": user.id if current_user.role in [UserRole.OWNER, UserRole.ADMINISTRATOR] else None,
        "username": user.username,
        "additional_usernames": additional_usernames if user.role in [UserRole.OWNER, UserRole.ADMINISTRATOR] else [],
        "role": user.role.value,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "created_at": user.created_at.isoformat()
    }


@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update current user's profile
    
    - **bio**: User bio (max 500 characters)
    - **avatar_url**: Avatar URL
    """
    result = await user_service.update_profile(
        db=db,
        user_id=current_user.id,
        bio=request.bio,
        avatar_url=request.avatar_url
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"success": True, "message": "Profile updated successfully"}


@router.put("/username")
async def update_username(
    request: UpdateUsernameRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update current user's username
    
    - **new_username**: New username (must be unique)
    """
    result = await user_service.update_username(
        db=db,
        user_id=current_user.id,
        new_username=request.new_username
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"success": True, "message": "Username updated successfully"}


@router.post("/additional-username")
async def add_additional_username(
    request: AddAdditionalUsernameRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Add additional username (Owner and Administrators only)
    
    - **username**: Additional username to add
    """
    if current_user.role not in [UserRole.OWNER, UserRole.ADMINISTRATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Owner and Administrators can have additional usernames"
        )
    
    result = await user_service.add_additional_username(
        db=db,
        user_id=current_user.id,
        additional_username=request.username
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"success": True, "message": "Additional username added successfully"}


@router.delete("/additional-username/{username}")
async def remove_additional_username(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Remove additional username
    
    - **username**: Additional username to remove
    """
    result = await user_service.remove_additional_username(
        db=db,
        user_id=current_user.id,
        username_to_remove=username
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"success": True, "message": "Additional username removed successfully"}


@router.put("/role")
async def update_user_role(
    request: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update user role (Owner only)
    
    - **user_id**: ID of user to update
    - **new_role**: New role (user, verified, administrator)
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Owner can change user roles"
        )
    
    # Map string to UserRole enum
    role_map = {
        "user": UserRole.USER,
        "verified": UserRole.VERIFIED,
        "administrator": UserRole.ADMINISTRATOR,
        "owner": UserRole.OWNER
    }
    
    new_role = role_map.get(request.new_role)
    if not new_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    result = await user_service.update_user_role(
        db=db,
        user_id=request.user_id,
        new_role=new_role,
        admin_id=current_user.id
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"success": True, "message": "User role updated successfully"}


@router.get("/stats/count")
async def get_user_count(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get total number of users (authenticated users only)"""
    count = await user_service.get_user_count(db=db)
    return {"count": count}
