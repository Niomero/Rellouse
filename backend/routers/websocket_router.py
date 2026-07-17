"""
WebSocket Router
Handles WebSocket connections for real-time messaging
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging
import json

from database import get_db
from models import User, Message
from websocket_service import manager
from security import token_manager

router = APIRouter(tags=["WebSocket"])

logger = logging.getLogger(__name__)


async def get_user_from_token(token: str, db: AsyncSession) -> User:
    """Validate token and get user"""
    try:
        payload = token_manager.decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            return None
        
        stmt = select(User).where(User.id == int(user_id), User.is_active == True)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        return user
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time messaging
    Requires authentication token as query parameter
    """
    user = await get_user_from_token(token, db)
    
    if not user:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    await manager.connect(websocket, user.id)
    
    # Update user online status
    user.is_online = True
    user.last_seen = datetime.utcnow()
    await db.commit()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "ping":
                # Heartbeat - update last seen
                user.last_seen = datetime.utcnow()
                await db.commit()
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "typing":
                # Typing indicator
                recipient_id = data.get("recipient_id")
                is_typing = data.get("is_typing", True)
                
                if recipient_id:
                    await manager.send_typing_indicator(user.id, recipient_id, is_typing)
            
            elif message_type == "read":
                # Mark message as read
                message_id = data.get("message_id")
                
                if message_id:
                    stmt = select(Message).where(
                        Message.id == message_id,
                        Message.recipient_id == user.id
                    )
                    result = await db.execute(stmt)
                    message = result.scalar_one_or_none()
                    
                    if message and not message.is_read:
                        message.is_read = True
                        await db.commit()
                        
                        # Send read receipt to sender
                        if message.sender_id:
                            await manager.send_read_receipt(user.id, message.sender_id, message_id)
            
            elif message_type == "message":
                # This is handled by message_router.py send_message endpoint
                # WebSocket is only for receiving real-time updates
                pass
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        
        # Update user offline status
        user.is_online = False
        user.last_seen = datetime.utcnow()
        await db.commit()
        
        logger.info(f"User {user.id} disconnected")
    
    except Exception as e:
        logger.error(f"WebSocket error for user {user.id}: {e}")
        await manager.disconnect(websocket)
        
        # Update user offline status
        user.is_online = False
        user.last_seen = datetime.utcnow()
        await db.commit()