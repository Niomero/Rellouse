"""
Verification Service
Handles verification requests and the @Verify bot workflow
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models import VerificationRequest, User, UserRole
from bot_service import bot_service
from typing import Optional, List, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)


class VerificationService:
    """Service for handling user verification requests"""
    
    @staticmethod
    async def submit_verification_request(
        db: AsyncSession,
        user_id: int,
        description: str,
        telegram_links: Optional[List[str]] = None,
        social_links: Optional[List[str]] = None,
        website_links: Optional[List[str]] = None,
        additional_materials: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit a verification request
        Returns: {"success": bool, "request": VerificationRequest, "error": str}
        """
        try:
            # Get user
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Check if user already has verified status or higher
            if user.role in [UserRole.VERIFIED, UserRole.ADMINISTRATOR, UserRole.OWNER]:
                return {"success": False, "error": "User already has verified status or higher"}
            
            # Check if there's already a pending request
            existing_request = await db.execute(
                select(VerificationRequest).where(
                    and_(
                        VerificationRequest.user_id == user_id,
                        VerificationRequest.status == "pending"
                    )
                )
            )
            if existing_request.scalar_one_or_none():
                return {"success": False, "error": "You already have a pending verification request"}
            
            # Create verification request
            request = VerificationRequest(
                user_id=user_id,
                description=description,
                telegram_links=json.dumps(telegram_links) if telegram_links else None,
                social_links=json.dumps(social_links) if social_links else None,
                website_links=json.dumps(website_links) if website_links else None,
                additional_materials=additional_materials,
                status="pending"
            )
            
            db.add(request)
            await db.commit()
            await db.refresh(request)
            
            # Send confirmation message to user via @Verify bot
            await VerificationService._send_confirmation_message(db, user_id, request.id)
            
            # Notify administrators
            await VerificationService._notify_admins(db, user, request)
            
            logger.info(f"Verification request submitted: user_id={user_id}, request_id={request.id}")
            return {"success": True, "request": request}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error submitting verification request: {str(e)}")
            return {"success": False, "error": "Failed to submit verification request"}
    
    @staticmethod
    async def get_verification_request(
        db: AsyncSession,
        request_id: int
    ) -> Optional[VerificationRequest]:
        """Get verification request by ID"""
        try:
            result = await db.execute(
                select(VerificationRequest).where(VerificationRequest.id == request_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting verification request: {str(e)}")
            return None
    
    @staticmethod
    async def get_user_verification_requests(
        db: AsyncSession,
        user_id: int
    ) -> List[VerificationRequest]:
        """Get all verification requests for a user"""
        try:
            result = await db.execute(
                select(VerificationRequest)
                .where(VerificationRequest.user_id == user_id)
                .order_by(VerificationRequest.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user verification requests: {str(e)}")
            return []
    
    @staticmethod
    async def get_pending_requests(
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0
    ) -> List[VerificationRequest]:
        """Get all pending verification requests"""
        try:
            result = await db.execute(
                select(VerificationRequest)
                .where(VerificationRequest.status == "pending")
                .order_by(VerificationRequest.created_at.asc())
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting pending requests: {str(e)}")
            return []
    
    @staticmethod
    async def approve_verification_request(
        db: AsyncSession,
        request_id: int,
        admin_id: int,
        admin_comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approve a verification request and grant Verified status
        Returns: {"success": bool, "error": str}
        """
        try:
            # Get admin
            admin_result = await db.execute(
                select(User).where(User.id == admin_id)
            )
            admin = admin_result.scalar_one_or_none()
            
            if not admin or admin.role not in [UserRole.ADMINISTRATOR, UserRole.OWNER]:
                return {"success": False, "error": "Only administrators can approve verification requests"}
            
            # Get request
            request = await VerificationService.get_verification_request(db, request_id)
            if not request:
                return {"success": False, "error": "Verification request not found"}
            
            if request.status != "pending":
                return {"success": False, "error": "Request is not pending"}
            
            # Get user
            user_result = await db.execute(
                select(User).where(User.id == request.user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Update request
            request.status = "approved"
            request.reviewed_by = admin_id
            request.reviewed_at = db.bind.dialect.name == 'postgresql' and db.execute(select(db.func.now())).scalar() or None
            request.admin_comment = admin_comment
            
            # Grant Verified status
            user.role = UserRole.VERIFIED
            
            await db.commit()
            
            # Send approval message to user
            await VerificationService._send_approval_message(db, user.id, admin_comment)
            
            logger.info(f"Verification request approved: request_id={request_id}, user_id={user.id}, admin_id={admin_id}")
            return {"success": True}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error approving verification request: {str(e)}")
            return {"success": False, "error": "Failed to approve verification request"}
    
    @staticmethod
    async def reject_verification_request(
        db: AsyncSession,
        request_id: int,
        admin_id: int,
        admin_comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reject a verification request
        Returns: {"success": bool, "error": str}
        """
        try:
            # Get admin
            admin_result = await db.execute(
                select(User).where(User.id == admin_id)
            )
            admin = admin_result.scalar_one_or_none()
            
            if not admin or admin.role not in [UserRole.ADMINISTRATOR, UserRole.OWNER]:
                return {"success": False, "error": "Only administrators can reject verification requests"}
            
            # Get request
            request = await VerificationService.get_verification_request(db, request_id)
            if not request:
                return {"success": False, "error": "Verification request not found"}
            
            if request.status != "pending":
                return {"success": False, "error": "Request is not pending"}
            
            # Update request
            request.status = "rejected"
            request.reviewed_by = admin_id
            request.reviewed_at = db.bind.dialect.name == 'postgresql' and db.execute(select(db.func.now())).scalar() or None
            request.admin_comment = admin_comment
            
            await db.commit()
            
            # Send rejection message to user
            await VerificationService._send_rejection_message(db, request.user_id, admin_comment)
            
            logger.info(f"Verification request rejected: request_id={request_id}, admin_id={admin_id}")
            return {"success": True}
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error rejecting verification request: {str(e)}")
            return {"success": False, "error": "Failed to reject verification request"}
    
    @staticmethod
    async def _send_confirmation_message(db: AsyncSession, user_id: int, request_id: int):
        """Send confirmation message via @Verify bot"""
        try:
            message = f"""✅ Your verification request has been submitted successfully!

Request ID: {request_id}

Your application is now being reviewed by our administrators. You will receive a notification once your request has been processed.

Thank you for your patience!"""
            
            await bot_service.send_bot_message(db, "~1", user_id, message)
        except Exception as e:
            logger.error(f"Error sending confirmation message: {str(e)}")
    
    @staticmethod
    async def _send_approval_message(db: AsyncSession, user_id: int, admin_comment: Optional[str]):
        """Send approval message via @Verify bot"""
        try:
            message = f"""🎉 Congratulations! Your verification request has been approved!

You now have Verified status on Rellouse Messenger.

Your profile will display the verified badge."""
            
            if admin_comment:
                message += f"\n\nAdmin comment: {admin_comment}"
            
            await bot_service.send_bot_message(db, "~1", user_id, message)
        except Exception as e:
            logger.error(f"Error sending approval message: {str(e)}")
    
    @staticmethod
    async def _send_rejection_message(db: AsyncSession, user_id: int, admin_comment: Optional[str]):
        """Send rejection message via @Verify bot"""
        try:
            message = f"""❌ Your verification request has been reviewed and unfortunately was not approved at this time."""
            
            if admin_comment:
                message += f"\n\nAdmin comment: {admin_comment}"
            
            message += "\n\nYou may submit a new request in the future with additional information."
            
            await bot_service.send_bot_message(db, "~1", user_id, message)
        except Exception as e:
            logger.error(f"Error sending rejection message: {str(e)}")
    
    @staticmethod
    async def _notify_admins(db: AsyncSession, user: User, request: VerificationRequest):
        """Notify all administrators about new verification request"""
        try:
            # Get all administrators
            admins_result = await db.execute(
                select(User).where(
                    User.role.in_([UserRole.ADMINISTRATOR, UserRole.OWNER]),
                    User.is_active == True
                )
            )
            admins = admins_result.scalars().all()
            
            # Parse links
            telegram_links = json.loads(request.telegram_links) if request.telegram_links else []
            social_links = json.loads(request.social_links) if request.social_links else []
            website_links = json.loads(request.website_links) if request.website_links else []
            
            message = f"""📋 New Verification Request

User: {user.username} (ID: {user.id})
Request ID: {request.id}

Description:
{request.description}"""
            
            if telegram_links:
                message += f"\n\nTelegram: {', '.join(telegram_links)}"
            
            if social_links:
                message += f"\nSocial Media: {', '.join(social_links)}"
            
            if website_links:
                message += f"\nWebsites: {', '.join(website_links)}"
            
            if request.additional_materials:
                message += f"\n\nAdditional Materials:\n{request.additional_materials}"
            
            # Send to all admins
            for admin in admins:
                await bot_service.send_bot_message(db, "~1", admin.id, message)
                
        except Exception as e:
            logger.error(f"Error notifying admins: {str(e)}")


# Export service instance
verification_service = VerificationService()
