"""
Message Service
Handles message sending, receiving, and management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from models import Message, User, Bot
from security import message_encryption
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MessageService:
    """Service for message operations"""
    
    @staticmethod
    async def send_message(
        db: AsyncSession,
        sender_id: int,
        recipient_id: int,
        content: str
    ) -> Dict[str, Any]:
        """
        Send a message from one user to another
        Returns: {"success": bool, "message": Message, "error": str}
        """
        try:
            # Verify sender exists
            sender_result = await db.execute(
                select(User).where(User.id == sender_id, User.is_active == True)
            )
            sender = sender_result.scalar_one_or_none()
            if not sender:
                return {"success": False, "error": "Sender not found"}
            
            # Verify recipient exists
            recipient_result = await db.execute(
                select(User).where(User.id == recipient_id, User.is_active == True)
            )
            recipient = recipient_result.scalar_one_or_none()
            if not recipient:
                return {"success": False, "error": "Recipient not found"}
            
            # Encrypt message
            encrypted_content, key_id = message_encryption.encrypt_message(content)
            
            # Create message
            message = Message(
                sender_id=sender_id,
                recipient_id=recipient_id,
                encrypted_content=encrypted_content,
                encryption_key_id=key_id
            )
            
            db.add(message)
            await db.commit()
            await db.refresh(message)
            
            logger.info(f"Message sent: sender={sender_id}, recipient={recipient_id}, message_id={message.id}")
            return {"success": True, "message": message}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error sending message: {str(e)}")
            return {"success": False, "error": "Failed to send message"}
    
    @staticmethod
    async def get_message(
        db: AsyncSession,
        message_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a message by ID (only if user is sender or recipient)
        Returns decrypted message
        """
        try:
            result = await db.execute(
                select(Message).where(
                    Message.id == message_id,
                    or_(
                        Message.sender_id == user_id,
                        Message.recipient_id == user_id
                    ),
                    Message.deleted_at.is_(None)
                )
            )
            message = result.scalar_one_or_none()
            
            if not message:
                return None
            
            # Decrypt message
            try:
                decrypted_content = message_encryption.decrypt_message(message.encrypted_content)
            except Exception as e:
                logger.error(f"Failed to decrypt message {message_id}: {str(e)}")
                decrypted_content = "[Decryption failed]"
            
            return {
                "id": message.id,
                "sender_id": message.sender_id,
                "bot_sender_id": message.bot_sender_id,
                "recipient_id": message.recipient_id,
                "content": decrypted_content,
                "is_read": message.is_read,
                "created_at": message.created_at,
                "edited_at": message.edited_at
            }
            
        except Exception as e:
            logger.error(f"Error getting message: {str(e)}")
            return None
    
    @staticmethod
    async def get_conversation(
        db: AsyncSession,
        user1_id: int,
        user2_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get conversation between two users
        Returns list of decrypted messages
        """
        try:
            result = await db.execute(
                select(Message)
                .where(
                    or_(
                        and_(Message.sender_id == user1_id, Message.recipient_id == user2_id),
                        and_(Message.sender_id == user2_id, Message.recipient_id == user1_id)
                    ),
                    Message.deleted_at.is_(None)
                )
                .order_by(Message.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            messages = result.scalars().all()
            
            # Decrypt messages
            decrypted_messages = []
            for message in messages:
                try:
                    decrypted_content = message_encryption.decrypt_message(message.encrypted_content)
                except Exception as e:
                    logger.error(f"Failed to decrypt message {message.id}: {str(e)}")
                    decrypted_content = "[Decryption failed]"
                
                decrypted_messages.append({
                    "id": message.id,
                    "sender_id": message.sender_id,
                    "bot_sender_id": message.bot_sender_id,
                    "recipient_id": message.recipient_id,
                    "content": decrypted_content,
                    "is_read": message.is_read,
                    "created_at": message.created_at,
                    "edited_at": message.edited_at
                })
            
            return decrypted_messages
            
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            return []
    
    @staticmethod
    async def get_user_conversations(
        db: AsyncSession,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user (list of users they've messaged with)
        Returns list of conversation partners with last message
        """
        try:
            # Get all messages where user is sender or recipient
            result = await db.execute(
                select(Message)
                .where(
                    or_(
                        Message.sender_id == user_id,
                        Message.recipient_id == user_id
                    ),
                    Message.deleted_at.is_(None)
                )
                .order_by(Message.created_at.desc())
            )
            messages = result.scalars().all()
            
            # Group by conversation partner
            conversations = {}
            for message in messages:
                partner_id = message.recipient_id if message.sender_id == user_id else message.sender_id
                
                if partner_id not in conversations:
                    try:
                        decrypted_content = message_encryption.decrypt_message(message.encrypted_content)
                    except:
                        decrypted_content = "[Decryption failed]"
                    
                    conversations[partner_id] = {
                        "partner_id": partner_id,
                        "last_message": decrypted_content,
                        "last_message_time": message.created_at,
                        "is_read": message.is_read if message.recipient_id == user_id else True
                    }
            
            return list(conversations.values())
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            return []
    
    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        message_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Mark a message as read (only by recipient)
        Returns: {"success": bool, "error": str}
        """
        try:
            result = await db.execute(
                select(Message).where(
                    Message.id == message_id,
                    Message.recipient_id == user_id
                )
            )
            message = result.scalar_one_or_none()
            
            if not message:
                return {"success": False, "error": "Message not found"}
            
            message.is_read = True
            await db.commit()
            
            return {"success": True}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error marking message as read: {str(e)}")
            return {"success": False, "error": "Failed to mark message as read"}
    
    @staticmethod
    async def delete_message(
        db: AsyncSession,
        message_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Delete a message (soft delete, only by sender)
        Returns: {"success": bool, "error": str}
        """
        try:
            result = await db.execute(
                select(Message).where(
                    Message.id == message_id,
                    Message.sender_id == user_id
                )
            )
            message = result.scalar_one_or_none()
            
            if not message:
                return {"success": False, "error": "Message not found or you don't have permission"}
            
            from datetime import datetime
            message.deleted_at = datetime.utcnow()
            await db.commit()
            
            logger.info(f"Message deleted: message_id={message_id}, user_id={user_id}")
            return {"success": True}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting message: {str(e)}")
            return {"success": False, "error": "Failed to delete message"}
    
    @staticmethod
    async def get_unread_count(
        db: AsyncSession,
        user_id: int
    ) -> int:
        """Get count of unread messages for a user"""
        try:
            from sqlalchemy import func
            result = await db.execute(
                select(func.count(Message.id)).where(
                    Message.recipient_id == user_id,
                    Message.is_read == False,
                    Message.deleted_at.is_(None)
                )
            )
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            return 0


# Export service instance
message_service = MessageService()
