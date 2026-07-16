"""
Bot Service
Handles bot account management and bot-related operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Bot, Message, User
from security import message_encryption
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BotService:
    """Service for bot management and operations"""
    
    @staticmethod
    async def create_bot(
        db: AsyncSession,
        bot_id: str,
        username: str,
        display_name: str,
        description: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new bot account
        Returns: {"success": bool, "bot": Bot, "error": str}
        """
        try:
            # Ensure bot_id starts with ~
            if not bot_id.startswith("~"):
                bot_id = "~" + bot_id
            
            # Ensure username starts with @
            if not username.startswith("@"):
                username = "@" + username
            
            # Check if bot already exists
            existing = await db.execute(
                select(Bot).where(Bot.id == bot_id)
            )
            if existing.scalar_one_or_none():
                return {"success": False, "error": "Bot ID already exists"}
            
            # Check if username is taken
            username_check = await db.execute(
                select(Bot).where(Bot.username == username)
            )
            if username_check.scalar_one_or_none():
                return {"success": False, "error": "Username already taken"}
            
            # Create bot
            bot = Bot(
                id=bot_id,
                username=username,
                display_name=display_name,
                description=description,
                avatar_url=avatar_url
            )
            
            db.add(bot)
            await db.commit()
            await db.refresh(bot)
            
            logger.info(f"Bot created: {username} (ID: {bot_id})")
            return {"success": True, "bot": bot}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating bot: {str(e)}")
            return {"success": False, "error": "Failed to create bot"}
    
    @staticmethod
    async def get_bot_by_id(db: AsyncSession, bot_id: str) -> Optional[Bot]:
        """Get bot by ID"""
        try:
            result = await db.execute(
                select(Bot).where(Bot.id == bot_id, Bot.is_active == True)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting bot by ID {bot_id}: {str(e)}")
            return None
    
    @staticmethod
    async def get_bot_by_username(db: AsyncSession, username: str) -> Optional[Bot]:
        """Get bot by username"""
        try:
            # Normalize username
            if not username.startswith("@"):
                username = "@" + username
            
            result = await db.execute(
                select(Bot).where(Bot.username == username, Bot.is_active == True)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting bot by username {username}: {str(e)}")
            return None
    
    @staticmethod
    async def get_all_bots(db: AsyncSession) -> List[Bot]:
        """Get all active bots"""
        try:
            result = await db.execute(
                select(Bot).where(Bot.is_active == True).order_by(Bot.id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting all bots: {str(e)}")
            return []
    
    @staticmethod
    async def send_bot_message(
        db: AsyncSession,
        bot_id: str,
        recipient_id: int,
        message_content: str
    ) -> Dict[str, Any]:
        """
        Send a message from a bot to a user
        Returns: {"success": bool, "message": Message, "error": str}
        """
        try:
            # Verify bot exists
            bot = await BotService.get_bot_by_id(db, bot_id)
            if not bot:
                return {"success": False, "error": "Bot not found"}
            
            # Verify recipient exists
            recipient_result = await db.execute(
                select(User).where(User.id == recipient_id, User.is_active == True)
            )
            recipient = recipient_result.scalar_one_or_none()
            if not recipient:
                return {"success": False, "error": "Recipient not found"}
            
            # Encrypt message
            encrypted_content, key_id = message_encryption.encrypt_message(message_content)
            
            # Create message
            message = Message(
                bot_sender_id=bot_id,
                recipient_id=recipient_id,
                encrypted_content=encrypted_content,
                encryption_key_id=key_id
            )
            
            db.add(message)
            await db.commit()
            await db.refresh(message)
            
            logger.info(f"Bot message sent: bot={bot_id}, recipient={recipient_id}")
            return {"success": True, "message": message}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error sending bot message: {str(e)}")
            return {"success": False, "error": "Failed to send message"}
    
    @staticmethod
    async def update_bot(
        db: AsyncSession,
        bot_id: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update bot information
        Returns: {"success": bool, "error": str}
        """
        try:
            # Get bot
            bot = await BotService.get_bot_by_id(db, bot_id)
            if not bot:
                return {"success": False, "error": "Bot not found"}
            
            # Update fields
            if display_name is not None:
                bot.display_name = display_name
            
            if description is not None:
                bot.description = description
            
            if avatar_url is not None:
                bot.avatar_url = avatar_url
            
            await db.commit()
            
            logger.info(f"Bot updated: {bot_id}")
            return {"success": True}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating bot: {str(e)}")
            return {"success": False, "error": "Failed to update bot"}
    
    @staticmethod
    async def deactivate_bot(
        db: AsyncSession,
        bot_id: str
    ) -> Dict[str, Any]:
        """
        Deactivate a bot
        Returns: {"success": bool, "error": str}
        """
        try:
            # Get bot
            bot = await BotService.get_bot_by_id(db, bot_id)
            if not bot:
                return {"success": False, "error": "Bot not found"}
            
            # Deactivate
            bot.is_active = False
            await db.commit()
            
            logger.info(f"Bot deactivated: {bot_id}")
            return {"success": True}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deactivating bot: {str(e)}")
            return {"success": False, "error": "Failed to deactivate bot"}


# Export service instance
bot_service = BotService()
