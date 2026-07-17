"""
Verification Router
Handles verification request submission and management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List
from database import get_db
from auth import auth_service
from verification_service import verification_service
from models import UserRole
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/verification", tags=["Verification"])


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
class SubmitVerificationRequest(BaseModel):
    description: str = Field(..., min_length=50, max_length=2000)
    telegram_links: Optional[List[str]] = None
    social_links: Optional[List[str]] = None
    website_links: Optional[List[str]] = None
    additional_materials: Optional[str] = None


class ReviewVerificationRequest(BaseModel):
    request_id: int
    action: str = Field(..., pattern=r"^(approve|reject)$")
    admin_comment: Optional[str] = None


@router.post("/submit")
async def submit_verification(
    request: SubmitVerificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Submit a verification request
    
    - **description**: Detailed description (50-2000 characters)
    - **telegram_links**: List of Telegram channel/group links
    - **social_links**: List of social media profile links
    - **website_links**: List of website URLs
    - **additional_materials**: Any additional information
    """
    result = await verification_service.submit_verification_request(
        db=db,
        user_id=current_user.id,
        description=request.description,
        telegram_links=request.telegram_links,
        social_links=request.social_links,
        website_links=request.website_links,
        additional_materials=request.additional_materials
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    verification_request = result["request"]
    
    return {
        "success": True,
        "request_id": verification_request.id,
        "message": "Verification request submitted successfully"
    }


@router.get("/my-requests")
async def get_my_verification_requests(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all verification requests for current user
    """
    requests = await verification_service.get_user_verification_requests(
        db=db,
        user_id=current_user.id
    )
    
    import json
    result = []
    for req in requests:
        telegram_links = json.loads(req.telegram_links) if req.telegram_links else []
        social_links = json.loads(req.social_links) if req.social_links else []
        website_links = json.loads(req.website_links) if req.website_links else []
        
        result.append({
            "id": req.id,
            "description": req.description,
            "telegram_links": telegram_links,
            "social_links": social_links,
            "website_links": website_links,
            "additional_materials": req.additional_materials,
            "status": req.status,
            "admin_comment": req.admin_comment,
            "created_at": req.created_at.isoformat(),
            "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else None
        })
    
    return {"requests": result, "count": len(result)}


@router.get("/pending")
async def get_pending_requests(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all pending verification requests (Administrators and Owner only)
    
    - **limit**: Maximum results (default: 50)
    - **offset**: Pagination offset (default: 0)
    """
    if current_user.role not in [UserRole.ADMINISTRATOR, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators and Owner can view pending requests"
        )
    
    requests = await verification_service.get_pending_requests(
        db=db,
        limit=limit,
        offset=offset
    )
    
    import json
    result = []
    for req in requests:
        telegram_links = json.loads(req.telegram_links) if req.telegram_links else []
        social_links = json.loads(req.social_links) if req.social_links else []
        website_links = json.loads(req.website_links) if req.website_links else []
        
        result.append({
            "id": req.id,
            "user_id": req.user_id,
            "description": req.description,
            "telegram_links": telegram_links,
            "social_links": social_links,
            "website_links": website_links,
            "additional_materials": req.additional_materials,
            "status": req.status,
            "created_at": req.created_at.isoformat()
        })
    
    return {"requests": result, "count": len(result)}


@router.get("/{request_id}")
async def get_verification_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get specific verification request by ID
    
    - **request_id**: Verification request ID
    """
    req = await verification_service.get_verification_request(
        db=db,
        request_id=request_id
    )
    
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification request not found"
        )
    
    # Check permissions
    if req.user_id != current_user.id and current_user.role not in [UserRole.ADMINISTRATOR, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this request"
        )
    
    import json
    telegram_links = json.loads(req.telegram_links) if req.telegram_links else []
    social_links = json.loads(req.social_links) if req.social_links else []
    website_links = json.loads(req.website_links) if req.website_links else []
    
    return {
        "id": req.id,
        "user_id": req.user_id,
        "description": req.description,
        "telegram_links": telegram_links,
        "social_links": social_links,
        "website_links": website_links,
        "additional_materials": req.additional_materials,
        "status": req.status,
        "admin_comment": req.admin_comment,
        "reviewed_by": req.reviewed_by,
        "created_at": req.created_at.isoformat(),
        "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else None
    }


@router.post("/review")
async def review_verification_request(
    request: ReviewVerificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Review a verification request (Administrators and Owner only)
    
    - **request_id**: Verification request ID
    - **action**: "approve" or "reject"
    - **admin_comment**: Optional comment for the user
    """
    if current_user.role not in [UserRole.ADMINISTRATOR, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators and Owner can review verification requests"
        )
    
    if request.action == "approve":
        result = await verification_service.approve_verification_request(
            db=db,
            request_id=request.request_id,
            admin_id=current_user.id,
            admin_comment=request.admin_comment
        )
    else:  # reject
        result = await verification_service.reject_verification_request(
            db=db,
            request_id=request.request_id,
            admin_id=current_user.id,
            admin_comment=request.admin_comment
        )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {
        "success": True,
        "message": f"Verification request {request.action}d successfully"
    }
