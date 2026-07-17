"""
Debug Router
Temporary debugging endpoints - REMOVE IN PRODUCTION
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User
from security import password_hasher
from config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/debug", tags=["Debug"])


@router.get("/test-owner-login")
async def test_owner_login(
    password: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Test owner login credentials
    WARNING: This is a debug endpoint - remove in production!
    """
    try:
        # Find owner account
        result = await db.execute(
            select(User).where(User.id == 0)
        )
        owner = result.scalar_one_or_none()
        
        if not owner:
            return {
                "success": False,
                "message": "Owner account not found (ID: 0)"
            }
        
        # Test password
        password_match = password_hasher.verify_password(password, owner.password_hash)
        
        # Also test with configured password
        configured_password_match = password_hasher.verify_password(
            settings.OWNER_PASSWORD, 
            owner.password_hash
        )
        
        return {
            "success": True,
            "owner_id": owner.id,
            "owner_login": owner.login,
            "owner_username": owner.username,
            "is_active": owner.is_active,
            "password_provided_matches": password_match,
            "configured_password_matches": configured_password_match,
            "configured_password": settings.OWNER_PASSWORD,
            "password_hash_length": len(owner.password_hash) if owner.password_hash else 0,
            "password_hash_starts_with": owner.password_hash[:10] if owner.password_hash else None
        }
        
    except Exception as e:
        logger.error(f"Debug test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
