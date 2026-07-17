"""
Bot Router
Handles bot-related operations and information
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List
from database import get_db
from auth import auth_service
from bot_service import bot_service
from models import UserRole
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/bots", tags=["Bots"])


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
class CreateBotRequest(BaseModel):
    bot_id: str = Field(..., pattern=r"^~\d+$")
    username: str = Field(..., min_length=5, max_length=17)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    avatar_url: Optional[str] = None


class UpdateBotRequest(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    avatar_url: Optional[str] = None


@router.get("/list")
async def get_all_bots(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get list of all active bots
    """
    bots = await bot_service.get_all_bots(db=db)
    
    result = []
    for bot in bots:
        result.append({
            "id": bot.id,
            "username": bot.username,
            "display_name": bot.display_name,
            "description": bot.description,
            "avatar_url": bot.avatar_url,
            "created_at": bot.created_at.isoformat()
        })
    
    return {"bots": result, "count": len(result)}


@router.get("/{bot_id}")
async def get_bot(
    bot_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get bot information by ID
    
    - **bot_id**: Bot ID (e.g., ~1, ~2)
    """
    bot = await bot_service.get_bot_by_id(db=db, bot_id=bot_id)
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    return {
        "id": bot.id,
        "username": bot.username,
        "display_name": bot.display_name,
        "description": bot.description,
        "avatar_url": bot.avatar_url,
        "created_at": bot.created_at.isoformat()
    }


@router.post("/create")
async def create_bot(
    request: CreateBotRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new bot (Owner only)
    
    - **bot_id**: Bot ID starting with ~ (e.g., ~1, ~2)
    - **username**: Bot username
    - **display_name**: Bot display name
    - **description**: Bot description
    - **avatar_url**: Bot avatar URL
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Owner can create bots"
        )
    
    result = await bot_service.create_bot(
        db=db,
        bot_id=request.bot_id,
        username=request.username,
        display_name=request.display_name,
        description=request.description,
        avatar_url=request.avatar_url
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    bot = result["bot"]
    
    return {
        "success": True,
        "bot": {
            "id": bot.id,
            "username": bot.username,
            "display_name": bot.display_name
        }
    }


@router.put("/{bot_id}")
async def update_bot(
    bot_id: str,
    request: UpdateBotRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update bot information (Owner only)
    
    - **bot_id**: Bot ID
    - **display_name**: New display name
    - **description**: New description
    - **avatar_url**: New avatar URL
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Owner can update bots"
        )
    
    result = await bot_service.update_bot(
        db=db,
        bot_id=bot_id,
        display_name=request.display_name,
        description=request.description,
        avatar_url=request.avatar_url
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"success": True, "message": "Bot updated successfully"}


@router.delete("/{bot_id}")
async def deactivate_bot(
    bot_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Deactivate a bot (Owner only)
    
    - **bot_id**: Bot ID
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Owner can deactivate bots"
        )
    
    result = await bot_service.deactivate_bot(db=db, bot_id=bot_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"success": True, "message": "Bot deactivated successfully"}
