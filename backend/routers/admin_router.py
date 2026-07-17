"""
Admin Router
Administrative endpoints for system management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import User
from security import password_hasher
from config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class UpdateOwnerPasswordRequest(BaseModel):
    new_password: str
    secret_key: str  # Simple authentication


class UpdateOwnerPasswordResponse(BaseModel):
    success: bool
    message: str
    username: Optional[str] = None


@router.post("/update-owner-password", response_model=UpdateOwnerPasswordResponse)
async def update_owner_password(
    request: UpdateOwnerPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update owner account password
    Requires secret_key for authentication
    """
    try:
        # Simple authentication check
        if request.secret_key != settings.SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid secret key"
            )
        
        # Find owner account (ID: 0)
        result = await db.execute(
            select(User).where(User.id == 0)
        )
        owner = result.scalar_one_or_none()
        
        if not owner:
            return UpdateOwnerPasswordResponse(
                success=False,
                message="Owner account not found (ID: 0)"
            )
        
        # Hash new password
        new_password_hash = password_hasher.hash_password(request.new_password)
        
        # Update password
        owner.password_hash = new_password_hash
        
        await db.commit()
        
        logger.info(f"✅ Owner password updated via API for user: {owner.username}")
        
        return UpdateOwnerPasswordResponse(
            success=True,
            message="Owner password updated successfully",
            username=owner.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update owner password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update password: {str(e)}"
        )


@router.get("/owner-info")
async def get_owner_info(
    secret_key: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get owner account information
    Requires secret_key for authentication
    """
    try:
        # Simple authentication check
        if secret_key != settings.SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid secret key"
            )
        
        # Find owner account (ID: 0)
        result = await db.execute(
            select(User).where(User.id == 0)
        )
        owner = result.scalar_one_or_none()
        
        if not owner:
            return {
                "success": False,
                "message": "Owner account not found"
            }
        
        return {
            "success": True,
            "id": owner.id,
            "username": owner.username,
            "login": owner.login,
            "role": owner.role.value,
            "is_active": owner.is_active,
            "created_at": owner.created_at.isoformat() if owner.created_at else None,
            "message": "Use the configured password from settings.OWNER_PASSWORD to login"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get owner info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get owner info: {str(e)}"
        )
