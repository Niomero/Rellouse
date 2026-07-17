"""
Message Router
Handles message sending, receiving, and conversation management with real-time WebSocket support
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging

from database import get_db
from models import User, Message, MessageAttachment
from auth import get_current_user
from security import encryption_manager
from websocket_service import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/messages", tags=["messages"])


# Request/Response Models
class SendMessageRequest(BaseModel):
    recipient_id: int
    content: str = Field(..., min_length=1, max_length=10000)
    attachment_urls: Optional[List[str]] = None


class MessageResponse(BaseModel):
    id: int
    sender_id: Optional[int]
    recipient_id: int
    content: str
    is_read: bool
    created_at: datetime
    edited_at: Optional[datetime]
    attachments: List[dict] = []
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    user_id: int
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    is_online: bool
    last_message: Optional[MessageResponse]
    unread_count: int


@router.post("/send", response_model=MessageResponse)
async def send_message(
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to another user with real-time delivery
    """
    # Verify recipient exists
    stmt = select(User).where(User.id == request.recipient_id, User.is_active == True)
    result = await db.execute(stmt)
    recipient = result.scalar_one_or_none()
    
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Encrypt message content
    encrypted_content = encryption_manager.encrypt(request.content)
    
    # Create message
    message = Message(
        sender_id=current_user.id,
        recipient_id=request.recipient_id,
        encrypted_content=encrypted_content,
        encryption_key_id="default",
        is_read=False,
        created_at=datetime.utcnow()
    )
    
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    # Handle attachments if provided
    attachments = []
    if request.attachment_urls:
        for url in request.attachment_urls:
            attachment = MessageAttachment(
                message_id=message.id,
                file_url=url,
                file_name=url.split("/")[-1],
                file_size=0,  # Will be updated by upload endpoint
                file_type="image/jpeg",  # Will be updated by upload endpoint
                encrypted=False
            )
            db.add(attachment)
            attachments.append({
                "file_url": url,
                "file_name": attachment.file_name,
                "file_type": attachment.file_type
            })
        
        await db.commit()
    
    # Send real-time notification to recipient
    message_data = {
        "id": message.id,
        "sender_id": current_user.id,
        "sender_username": current_user.username,
        "sender_display_name": current_user.display_name,
        "sender_avatar": current_user.avatar_url,
        "content": request.content,
        "attachments": attachments,
        "created_at": message.created_at.isoformat(),
        "is_read": False
    }
    
    await manager.send_message_notification(current_user.id, request.recipient_id, message_data)
    
    return MessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        recipient_id=message.recipient_id,
        content=request.content,
        is_read=message.is_read,
        created_at=message.created_at,
        edited_at=message.edited_at,
        attachments=attachments
    )


@router.get("/conversation/{user_id}", response_model=List[MessageResponse])
async def get_conversation(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation history with another user
    """
    stmt = select(Message).where(
        or_(
            and_(Message.sender_id == current_user.id, Message.recipient_id == user_id),
            and_(Message.sender_id == user_id, Message.recipient_id == current_user.id)
        ),
        Message.deleted_at.is_(None)
    ).order_by(Message.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    messages = result.scalars().all()
    
    # Decrypt messages and format response
    response = []
    for msg in reversed(messages):  # Reverse to show oldest first
        try:
            decrypted_content = encryption_manager.decrypt(msg.encrypted_content)
        except:
            decrypted_content = "[Encrypted message]"
        
        # Get attachments
        attachments = []
        for att in msg.attachments:
            attachments.append({
                "file_url": att.file_url,
                "file_name": att.file_name,
                "file_type": att.file_type,
                "thumbnail_url": att.thumbnail_url
            })
        
        response.append(MessageResponse(
            id=msg.id,
            sender_id=msg.sender_id,
            recipient_id=msg.recipient_id,
            content=decrypted_content,
            is_read=msg.is_read,
            created_at=msg.created_at,
            edited_at=msg.edited_at,
            attachments=attachments
        ))
    
    return response


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all conversations with last message and unread count
    """
    # Get all users the current user has conversations with
    stmt = select(Message.sender_id, Message.recipient_id).where(
        or_(
            Message.sender_id == current_user.id,
            Message.recipient_id == current_user.id
        ),
        Message.deleted_at.is_(None)
    ).distinct()
    
    result = await db.execute(stmt)
    message_pairs = result.all()
    
    # Extract unique user IDs
    user_ids = set()
    for sender_id, recipient_id in message_pairs:
        if sender_id != current_user.id:
            user_ids.add(sender_id)
        if recipient_id != current_user.id:
            user_ids.add(recipient_id)
    
    conversations = []
    
    for user_id in user_ids:
        # Get user info
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            continue
        
        # Get last message
        stmt = select(Message).where(
            or_(
                and_(Message.sender_id == current_user.id, Message.recipient_id == user_id),
                and_(Message.sender_id == user_id, Message.recipient_id == current_user.id)
            ),
            Message.deleted_at.is_(None)
        ).order_by(Message.created_at.desc()).limit(1)
        
        result = await db.execute(stmt)
        last_message = result.scalar_one_or_none()
        
        last_msg_response = None
        if last_message:
            try:
                decrypted_content = encryption_manager.decrypt(last_message.encrypted_content)
            except:
                decrypted_content = "[Encrypted message]"
            
            last_msg_response = MessageResponse(
                id=last_message.id,
                sender_id=last_message.sender_id,
                recipient_id=last_message.recipient_id,
                content=decrypted_content,
                is_read=last_message.is_read,
                created_at=last_message.created_at,
                edited_at=last_message.edited_at,
                attachments=[]
            )
        
        # Get unread count
        stmt = select(func.count(Message.id)).where(
            Message.sender_id == user_id,
            Message.recipient_id == current_user.id,
            Message.is_read == False,
            Message.deleted_at.is_(None)
        )
        result = await db.execute(stmt)
        unread_count = result.scalar() or 0
        
        conversations.append(ConversationResponse(
            user_id=user.id,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            is_online=user.is_online,
            last_message=last_msg_response,
            unread_count=unread_count
        ))
    
    # Sort by last message time
    conversations.sort(
        key=lambda x: x.last_message.created_at if x.last_message else datetime.min,
        reverse=True
    )
    
    return conversations


@router.put("/{message_id}/read")
async def mark_as_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a message as read
    """
    stmt = select(Message).where(
        Message.id == message_id,
        Message.recipient_id == current_user.id
    )
    result = await db.execute(stmt)
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if not message.is_read:
        message.is_read = True
        await db.commit()
        
        # Send read receipt via WebSocket
        if message.sender_id:
            await manager.send_read_receipt(current_user.id, message.sender_id, message_id)
    
    return {"success": True, "message": "Message marked as read"}


@router.get("/unread/count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get total unread message count
    """
    stmt = select(func.count(Message.id)).where(
        Message.recipient_id == current_user.id,
        Message.is_read == False,
        Message.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    count = result.scalar() or 0
    
    return {"unread_count": count}


@router.post("/upload", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an image for message attachment
    Returns temporary URL (implement actual storage later)
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")
    
    # Validate file size (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    
    # TODO: Implement actual file storage (S3, local storage, etc.)
    # For now, return a placeholder URL
    file_url = f"/uploads/images/{current_user.id}/{file.filename}"
    
    return {
        "success": True,
        "file_url": file_url,
        "file_name": file.filename,
        "file_size": len(content),
        "file_type": file.content_type
    }