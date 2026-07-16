"""
Message Router
Handles message sending, receiving, and conversation management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List
from database import get_db
from auth import auth_service
from message_service import message_service
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
class SendMessageRequest(BaseModel):
    recipient_id: int
    content: str = Field(..., min_length=1, max_length=10000)


@router.post("/send")
async def send_message(
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Send a message to another user
    
    - **recipient_id**: ID of the recipient user
    - **content**: Message content (1-10000 characters)
    """
    result = await message_service.send_message(
        db=db,
        sender_id=current_user.id,
        recipient_id=request.recipient_id,
        content=request.content
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    message = result["message"]
    
    return {
        "success": True,
        "message_id": message.id,
        "created_at": message.created_at.isoformat()
    }


@router.get("/{message_id}")
async def get_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a specific message by ID
    
    - **message_id**: ID of the message
    """
    message = await message_service.get_message(
        db=db,
        message_id=message_id,
        user_id=current_user.id
    )
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or you don't have access"
        )
    
    return message


@router.get("/conversation/{user_id}")
async def get_conversation(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get conversation with another user
    
    - **user_id**: ID of the other user
    - **limit**: Maximum messages to return (default: 50)
    - **offset**: Pagination offset (default: 0)
    """
    messages = await message_service.get_conversation(
        db=db,
        user1_id=current_user.id,
        user2_id=user_id,
        limit=limit,
        offset=offset
    )
    
    return {
        "messages": messages,
        "count": len(messages)
    }


@router.get("/conversations/list")
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get list of all conversations for current user
    """
    conversations = await message_service.get_user_conversations(
        db=db,
        user_id=current_user.id
    )
    
    return {
        "conversations": conversations,
        "count": len(conversations)
    }


@router.put("/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mark a message as read
    
    - **message_id**: ID of the message
    """
    result = await message_service.mark_as_read(
        db=db,
        message_id=message_id,
        user_id=current_user.id
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"success": True, "message": "Message marked as read"}


@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a message (soft delete, sender only)
    
    - **message_id**: ID of the message
    """
    result = await message_service.delete_message(
        db=db,
        message_id=message_id,
        user_id=current_user.id
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {"success": True, "message": "Message deleted successfully"}


@router.get("/unread/count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get count of unread messages for current user
    """
    count = await message_service.get_unread_count(
        db=db,
        user_id=current_user.id
    )
    
    return {"unread_count": count}
