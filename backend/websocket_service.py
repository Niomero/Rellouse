"""
WebSocket Service
Handles real-time messaging and online status
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time messaging"""
    
    def __init__(self):
        # user_id -> Set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # websocket -> user_id mapping
        self.connection_user_map: Dict[WebSocket, int] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a user's websocket"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.connection_user_map[websocket] = user_id
        
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
        
        # Notify user's contacts that they are online
        await self.broadcast_status(user_id, "online")
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect a user's websocket"""
        user_id = self.connection_user_map.get(websocket)
        
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # If no more connections, remove user and broadcast offline status
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                await self.broadcast_status(user_id, "offline")
                logger.info(f"User {user_id} disconnected (all connections closed)")
            else:
                logger.info(f"User {user_id} connection closed. Remaining: {len(self.active_connections[user_id])}")
        
        if websocket in self.connection_user_map:
            del self.connection_user_map[websocket]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user (all their connections)"""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                await self.disconnect(conn)
    
    async def broadcast_status(self, user_id: int, status: str):
        """Broadcast user status change to all connected users"""
        message = {
            "type": "status_change",
            "user_id": user_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all connected users
        for uid in list(self.active_connections.keys()):
            if uid != user_id:  # Don't send to the user themselves
                await self.send_personal_message(message, uid)
    
    async def send_message_notification(self, sender_id: int, recipient_id: int, message_data: dict):
        """Send new message notification to recipient"""
        notification = {
            "type": "new_message",
            "sender_id": sender_id,
            "message": message_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_personal_message(notification, recipient_id)
    
    async def send_typing_indicator(self, sender_id: int, recipient_id: int, is_typing: bool):
        """Send typing indicator to recipient"""
        indicator = {
            "type": "typing_indicator",
            "user_id": sender_id,
            "is_typing": is_typing,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_personal_message(indicator, recipient_id)
    
    async def send_read_receipt(self, reader_id: int, sender_id: int, message_id: int):
        """Send read receipt to message sender"""
        receipt = {
            "type": "read_receipt",
            "message_id": message_id,
            "reader_id": reader_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_personal_message(receipt, sender_id)
    
    def is_user_online(self, user_id: int) -> bool:
        """Check if a user is currently online"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    def get_online_users(self) -> list[int]:
        """Get list of all online user IDs"""
        return list(self.active_connections.keys())


# Global connection manager instance
manager = ConnectionManager()
