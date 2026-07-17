"""
Authentication Service
Handles user registration, login, and session management
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from models import User, Session, SecurityLog, UserRole
from security import password_hasher, token_manager, username_validator, security_validator
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    async def register_user(
        db: AsyncSession,
        login: str,
        password: str,
        username: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user
        Returns: {"success": bool, "user": User, "error": str}
        """
        try:
            # Validate username
            is_valid, error = username_validator.validate_username(username)
            if not is_valid:
                await AuthService._log_security_event(
                    db, None, "registration_failed", ip_address, user_agent,
                    {"reason": "invalid_username", "error": error}, "warning"
                )
                return {"success": False, "error": error}
            
            # Normalize username
            username = username_validator.normalize_username(username)
            
            # Check if username already exists
            existing_user = await db.execute(
                select(User).where(User.username == username)
            )
            if existing_user.scalar_one_or_none():
                await AuthService._log_security_event(
                    db, None, "registration_failed", ip_address, user_agent,
                    {"reason": "username_taken", "username": username}, "warning"
                )
                return {"success": False, "error": "Username is already taken"}
            
            # Check if login already exists
            existing_login = await db.execute(
                select(User).where(User.login == login)
            )
            if existing_login.scalar_one_or_none():
                await AuthService._log_security_event(
                    db, None, "registration_failed", ip_address, user_agent,
                    {"reason": "login_taken", "login": login}, "warning"
                )
                return {"success": False, "error": "Login is already taken"}
            
            # Validate password strength
            is_valid, error = security_validator.validate_password_strength(password)
            if not is_valid:
                await AuthService._log_security_event(
                    db, None, "registration_failed", ip_address, user_agent,
                    {"reason": "weak_password"}, "warning"
                )
                return {"success": False, "error": error}
            
            # Hash password
            password_hash = password_hasher.hash_password(password)
            
            # Create user
            new_user = User(
                login=login,
                password_hash=password_hash,
                username=username,
                role=UserRole.USER
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            # Log successful registration
            await AuthService._log_security_event(
                db, new_user.id, "registration_success", ip_address, user_agent,
                {"username": username}, "info"
            )
            
            logger.info(f"User registered successfully: {username} (ID: {new_user.id})")
            return {"success": True, "user": new_user}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Registration error: {str(e)}")
            return {"success": False, "error": "Registration failed. Please try again."}
    
    @staticmethod
    async def login_user(
        db: AsyncSession,
        login: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate user and create session
        Returns: {"success": bool, "access_token": str, "refresh_token": str, "user": User, "error": str}
        """
        try:
            # Find user by login
            result = await db.execute(
                select(User).where(User.login == login)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await AuthService._log_security_event(
                    db, None, "login_failed", ip_address, user_agent,
                    {"reason": "user_not_found", "login": login}, "warning"
                )
                return {"success": False, "error": "Invalid login or password"}
            
            # Verify password
            if not password_hasher.verify_password(password, user.password_hash):
                await AuthService._log_security_event(
                    db, user.id, "login_failed", ip_address, user_agent,
                    {"reason": "invalid_password"}, "warning"
                )
                return {"success": False, "error": "Invalid login or password"}
            
            # Check if user is active
            if not user.is_active:
                await AuthService._log_security_event(
                    db, user.id, "login_failed", ip_address, user_agent,
                    {"reason": "account_inactive"}, "warning"
                )
                return {"success": False, "error": "Account is inactive"}
            
            # Create tokens
            token_data = {"sub": str(user.id), "username": user.username, "role": user.role.value}
            access_token = token_manager.create_access_token(token_data)
            refresh_token = token_manager.create_refresh_token(token_data)
            
            # Create session
            expires_at = datetime.utcnow() + timedelta(days=7)
            session = Session(
                user_id=user.id,
                token=access_token,
                refresh_token=refresh_token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at
            )
            
            db.add(session)
            
            # Update last login
            user.last_login = datetime.utcnow()
            
            await db.commit()
            
            # Log successful login
            await AuthService._log_security_event(
                db, user.id, "login_success", ip_address, user_agent,
                {"username": user.username}, "info"
            )
            
            logger.info(f"User logged in successfully: {user.username} (ID: {user.id})")
            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Login error: {str(e)}")
            return {"success": False, "error": "Login failed. Please try again."}
    
    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token: str
    ) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        Returns: {"success": bool, "access_token": str, "error": str}
        """
        try:
            # Verify refresh token
            payload = token_manager.verify_token(refresh_token, "refresh")
            if not payload:
                return {"success": False, "error": "Invalid or expired refresh token"}
            
            user_id = int(payload.get("sub"))
            
            # Find session
            result = await db.execute(
                select(Session).where(
                    Session.refresh_token == refresh_token,
                    Session.user_id == user_id,
                    Session.is_active == True
                )
            )
            session = result.scalar_one_or_none()
            
            if not session:
                return {"success": False, "error": "Session not found or expired"}
            
            # Check if session is expired
            if session.expires_at < datetime.utcnow():
                session.is_active = False
                await db.commit()
                return {"success": False, "error": "Session expired"}
            
            # Get user
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.is_active:
                return {"success": False, "error": "User not found or inactive"}
            
            # Create new access token
            token_data = {"sub": str(user.id), "username": user.username, "role": user.role.value}
            access_token = token_manager.create_access_token(token_data)
            
            # Update session
            session.token = access_token
            session.last_activity = datetime.utcnow()
            
            await db.commit()
            
            return {"success": True, "access_token": access_token}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Token refresh error: {str(e)}")
            return {"success": False, "error": "Token refresh failed"}
    
    @staticmethod
    async def logout_user(
        db: AsyncSession,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Logout user and invalidate session
        Returns: {"success": bool, "error": str}
        """
        try:
            # Find and deactivate session
            result = await db.execute(
                select(Session).where(
                    Session.token == access_token,
                    Session.is_active == True
                )
            )
            session = result.scalar_one_or_none()
            
            if session:
                session.is_active = False
                await db.commit()
                
                logger.info(f"User logged out: user_id={session.user_id}")
            
            return {"success": True}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Logout error: {str(e)}")
            return {"success": False, "error": "Logout failed"}
    
    @staticmethod
    async def get_current_user(
        db: AsyncSession,
        access_token: str
    ) -> Optional[User]:
        """Get current user from access token"""
        try:
            # Verify token
            payload = token_manager.verify_token(access_token, "access")
            if not payload:
                return None
            
            user_id = int(payload.get("sub"))
            
            # Get user
            result = await db.execute(
                select(User).where(User.id == user_id, User.is_active == True)
            )
            user = result.scalar_one_or_none()
            
            return user
            
        except Exception as e:
            logger.error(f"Get current user error: {str(e)}")
            return None
    
    @staticmethod
    async def _log_security_event(
        db: AsyncSession,
        user_id: Optional[int],
        event_type: str,
        ip_address: Optional[str],
        user_agent: Optional[str],
        details: Dict[str, Any],
        severity: str = "info"
    ):
        """Log security event"""
        try:
            log_entry = SecurityLog(
                user_id=user_id,
                event_type=event_type,
                ip_address=ip_address,
                user_agent=user_agent,
                details=json.dumps(details),
                severity=severity
            )
            db.add(log_entry)
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")


# Export service instance
auth_service = AuthService()
