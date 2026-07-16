"""
WebSocket Router
Handles real-time messaging via WebSocket connections
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Set
from database import get_db
from auth import auth_service
from message_service import message_service
from config import settings
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time messaging"""
    
    def __init__(self):
        # user_id -> Set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Add a new WebSocket connection for a user"""
        await websocket.accept()
        
        async with self.lock:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            
            # Check connection limit
            if len(self.active_connections[user_id]) >= settings.WS_MAX_CONNECTIONS_PER_USER:
                await websocket.close(code=1008, reason="Maximum connections reached")
                return False
            
            self.active_connections[user_id].add(websocket)
            logger.info(f"WebSocket connected: user_id={user_id}, total_connections={len(self.active_connections[user_id])}")
            return True
    
    async def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove a WebSocket connection"""
        async with self.lock:
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                
                # Clean up empty sets
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                
                logger.info(f"WebSocket disconnected: user_id={user_id}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to all connections of a specific user"""
        if user_id not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {str(e)}")
                disconnected.add(connection)
        
        # Clean up disconnected connections
        if disconnected:
            async with self.lock:
                self.active_connections[user_id] -= disconnected
    
    async def broadcast_to_users(self, message: dict, user_ids: list):
        """Broadcast a message to multiple users"""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    def get_active_users(self) -> list:
        """Get list of currently connected user IDs"""
        return list(self.active_connections.keys())
    
    def is_user_online(self, user_id: int) -> bool:
        """Check if a user has any active connections"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# Global connection manager
manager = ConnectionManager()


async def verify_websocket_token(token: str, db: AsyncSession) -> int:
    """Verify WebSocket authentication token and return user_id"""
    try:
        user = await auth_service.get_current_user(db=db, access_token=token)
        if user:
            return user.id
        return None
    except Exception as e:
        logger.error(f"WebSocket token verification failed: {str(e)}")
        return None


@router.websocket("/chat")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="Authentication token")
):
    """
    WebSocket endpoint for real-time messaging
    
    Query Parameters:
    - token: JWT access token for authentication
    
    Message Format (Client -> Server):
    {
        "type": "message",
        "recipient_id": 123,
        "content": "Hello!"
    }
    
    Message Format (Server -> Client):
    {
        "type": "message",
        "message_id": 456,
        "sender_id": 789,
        "content": "Hello!",
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    Heartbeat (Server -> Client):
    {
        "type": "heartbeat",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    """
    db = None
    user_id = None
    
    try:
        # Get database session
        async for session in get_db():
            db = session
            break
        
        # Verify authentication
        user_id = await verify_websocket_token(token, db)
        if not user_id:
            await websocket.close(code=1008, reason="Authentication failed")
            return
        
        # Connect user
        connected = await manager.connect(websocket, user_id)
        if not connected:
            return
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "message": "Connected successfully"
        })
        
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(send_heartbeat(websocket, user_id))
        
        try:
            # Message handling loop
            while True:
                # Receive message from client
                data = await websocket.receive_json()
                
                message_type = data.get("type")
                
                if message_type == "message":
                    # Handle new message
                    recipient_id = data.get("recipient_id")
                    content = data.get("content")
                    
                    if not recipient_id or not content:
                        await websocket.send_json({
                            "type": "error",
                            "error": "Missing recipient_id or content"
                        })
                        continue
                    
                    # Send message via service
                    result = await message_service.send_message(
                        db=db,
                        sender_id=user_id,
                        recipient_id=recipient_id,
                        content=content
                    )
                    
                    if result["success"]:
                        message = result["message"]
                        
                        # Notify sender (confirmation)
                        await websocket.send_json({
                            "type": "message_sent",
                            "message_id": message.id,
                            "recipient_id": recipient_id,
                            "created_at": message.created_at.isoformat()
                        })
                        
                        # Notify recipient (if online)
                        await manager.send_personal_message({
                            "type": "message",
                            "message_id": message.id,
                            "sender_id": user_id,
                            "content": content,
                            "created_at": message.created_at.isoformat()
                        }, recipient_id)
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "error": result["error"]
                        })
                
                elif message_type == "typing":
                    # Handle typing indicator
                    recipient_id = data.get("recipient_id")
                    if recipient_id:
                        await manager.send_personal_message({
                            "type": "typing",
                            "user_id": user_id
                        }, recipient_id)
                
                elif message_type == "read":
                    # Handle read receipt
                    message_id = data.get("message_id")
                    if message_id:
                        await message_service.mark_as_read(
                            db=db,
                            message_id=message_id,
                            user_id=user_id
                        )
                
                elif message_type == "ping":
                    # Handle ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": data.get("timestamp")
                    })
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Unknown message type: {message_type}"
                    })
        
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected normally: user_id={user_id}")
        
        finally:
            # Cancel heartbeat task
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
    
    finally:
        # Disconnect user
        if user_id:
            await manager.disconnect(websocket, user_id)
        
        # Close database session
        if db:
            await db.close()


async def send_heartbeat(websocket: WebSocket, user_id: int):
    """Send periodic heartbeat to keep connection alive"""
    try:
        while True:
            await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
            
            from datetime import datetime
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    except asyncio.CancelledError:
        logger.debug(f"Heartbeat cancelled for user_id={user_id}")
    except Exception as e:
        logger.error(f"Heartbeat error for user_id={user_id}: {str(e)}")


@router.get("/online-users")
async def get_online_users():
    """Get list of currently online users (for debugging/admin)"""
    return {
        "online_users": manager.get_active_users(),
        "count": len(manager.get_active_users())
    }


@router.get("/user-status/{user_id}")
async def check_user_status(user_id: int):
    """Check if a specific user is online"""
    return {
        "user_id": user_id,
        "is_online": manager.is_user_online(user_id)
    }
