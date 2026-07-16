"""
User Service
Handles user profile management, username updates, and user queries
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from models import User, UserRole
from security import username_validator, security_validator
from typing import Optional, List, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)


class UserService:
    """Service for user profile and account management"""
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            result = await db.execute(
                select(User).where(User.id == user_id, User.is_active == True)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            return None
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            # Normalize username
            username = username_validator.normalize_username(username)
            
            result = await db.execute(
                select(User).where(User.username == username, User.is_active == True)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {str(e)}")
            return None
    
    @staticmethod
    async def search_users(
        db: AsyncSession,
        query: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[User]:
        """
        Search users by username
        Returns list of users matching the query
        """
        try:
            # Normalize query
            query = query.strip().lower()
            if not query.startswith("@"):
                query = "@" + query
            
            # Search by username (case-insensitive)
            result = await db.execute(
                select(User)
                .where(
                    User.username.ilike(f"%{query}%"),
                    User.is_active == True
                )
                .order_by(User.username)
                .limit(limit)
                .offset(offset)
            )
            
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching users: {str(e)}")
            return []
    
    @staticmethod
    async def update_username(
        db: AsyncSession,
        user_id: int,
        new_username: str
    ) -> Dict[str, Any]:
        """
        Update user's username
        Returns: {"success": bool, "error": str}
        """
        try:
            # Validate new username
            is_valid, error = username_validator.validate_username(new_username)
            if not is_valid:
                return {"success": False, "error": error}
            
            # Normalize username
            new_username = username_validator.normalize_username(new_username)
            
            # Check if username is already taken
            existing = await db.execute(
                select(User).where(User.username == new_username)
            )
            if existing.scalar_one_or_none():
                return {"success": False, "error": "Username is already taken"}
            
            # Get user
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Update username
            old_username = user.username
            user.username = new_username
            
            await db.commit()
            
            logger.info(f"Username updated: {old_username} -> {new_username} (user_id: {user_id})")
            return {"success": True}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating username: {str(e)}")
            return {"success": False, "error": "Failed to update username"}
    
    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user_id: int,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update user profile (bio, avatar)
        Returns: {"success": bool, "error": str}
        """
        try:
            # Get user
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Update fields
            if bio is not None:
                user.bio = security_validator.sanitize_input(bio, max_length=500)
            
            if avatar_url is not None:
                user.avatar_url = avatar_url
            
            await db.commit()
            
            logger.info(f"Profile updated for user_id: {user_id}")
            return {"success": True}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating profile: {str(e)}")
            return {"success": False, "error": "Failed to update profile"}
    
    @staticmethod
    async def add_additional_username(
        db: AsyncSession,
        user_id: int,
        additional_username: str
    ) -> Dict[str, Any]:
        """
        Add additional username (only for Owner and Administrators)
        Max 4 additional usernames
        Returns: {"success": bool, "error": str}
        """
        try:
            # Get user
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Check if user has permission
            if user.role not in [UserRole.OWNER, UserRole.ADMINISTRATOR]:
                return {"success": False, "error": "Only Owner and Administrators can have additional usernames"}
            
            # Validate username
            is_valid, error = username_validator.validate_username(additional_username)
            if not is_valid:
                return {"success": False, "error": error}
            
            # Normalize username
            additional_username = username_validator.normalize_username(additional_username)
            
            # Check if username is already taken
            existing = await db.execute(
                select(User).where(User.username == additional_username)
            )
            if existing.scalar_one_or_none():
                return {"success": False, "error": "Username is already taken"}
            
            # Parse existing additional usernames
            additional_usernames = []
            if user.additional_usernames:
                try:
                    additional_usernames = json.loads(user.additional_usernames)
                except:
                    additional_usernames = []
            
            # Check if already exists in additional usernames
            if additional_username in additional_usernames:
                return {"success": False, "error": "Username already in additional usernames"}
            
            # Check limit
            if len(additional_usernames) >= 4:
                return {"success": False, "error": "Maximum 4 additional usernames allowed"}
            
            # Add username
            additional_usernames.append(additional_username)
            user.additional_usernames = json.dumps(additional_usernames)
            
            await db.commit()
            
            logger.info(f"Additional username added: {additional_username} for user_id: {user_id}")
            return {"success": True}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error adding additional username: {str(e)}")
            return {"success": False, "error": "Failed to add additional username"}
    
    @staticmethod
    async def remove_additional_username(
        db: AsyncSession,
        user_id: int,
        username_to_remove: str
    ) -> Dict[str, Any]:
        """
        Remove additional username
        Returns: {"success": bool, "error": str}
        """
        try:
            # Get user
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Normalize username
            username_to_remove = username_validator.normalize_username(username_to_remove)
            
            # Parse existing additional usernames
            additional_usernames = []
            if user.additional_usernames:
                try:
                    additional_usernames = json.loads(user.additional_usernames)
                except:
                    additional_usernames = []
            
            # Remove username
            if username_to_remove not in additional_usernames:
                return {"success": False, "error": "Username not found in additional usernames"}
            
            additional_usernames.remove(username_to_remove)
            user.additional_usernames = json.dumps(additional_usernames) if additional_usernames else None
            
            await db.commit()
            
            logger.info(f"Additional username removed: {username_to_remove} for user_id: {user_id}")
            return {"success": True}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error removing additional username: {str(e)}")
            return {"success": False, "error": "Failed to remove additional username"}
    
    @staticmethod
    async def update_user_role(
        db: AsyncSession,
        user_id: int,
        new_role: UserRole,
        admin_id: int
    ) -> Dict[str, Any]:
        """
        Update user role (only Owner can do this)
        Returns: {"success": bool, "error": str}
        """
        try:
            # Get admin
            admin_result = await db.execute(
                select(User).where(User.id == admin_id)
            )
            admin = admin_result.scalar_one_or_none()
            
            if not admin or admin.role != UserRole.OWNER:
                return {"success": False, "error": "Only Owner can change user roles"}
            
            # Get user
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Cannot change Owner role
            if user.role == UserRole.OWNER:
                return {"success": False, "error": "Cannot change Owner role"}
            
            # Update role
            old_role = user.role
            user.role = new_role
            
            await db.commit()
            
            logger.info(f"User role updated: user_id={user_id}, {old_role} -> {new_role}")
            return {"success": True}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating user role: {str(e)}")
            return {"success": False, "error": "Failed to update user role"}
    
    @staticmethod
    async def get_user_count(db: AsyncSession) -> int:
        """Get total number of active users"""
        try:
            result = await db.execute(
                select(func.count(User.id)).where(User.is_active == True)
            )
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error getting user count: {str(e)}")
            return 0


# Export service instance
user_service = UserService()
