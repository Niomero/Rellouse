"""
System Initialization
Creates the owner account and system bots on first run
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User, UserRole
from security import password_hasher
from config import settings
import logging
import json

logger = logging.getLogger(__name__)


async def initialize_system(db: AsyncSession) -> bool:
    """
    Initialize the system with owner account and system bots
    Returns: True if initialization was performed, False if already initialized
    """
    try:
        # Check if owner already exists (ID: 0)
        result = await db.execute(
            select(User).where(User.id == 0)
        )
        owner = result.scalar_one_or_none()
        
        if owner:
            logger.info("System already initialized")
            return False
        
        logger.info("Initializing system for first time...")
        
        # Create owner account
        owner_password_hash = password_hasher.hash_password(settings.OWNER_PASSWORD)
        
        owner = User(
            id=0,
            login=settings.OWNER_USERNAME,
            password_hash=owner_password_hash,
            username=f"@{settings.OWNER_USERNAME}",
            display_name=settings.OWNER_USERNAME,
            additional_usernames=json.dumps([
                f"@{username}" for username in settings.owner_additional_usernames_list
            ]),
            role=UserRole.OWNER,
            bio="Owner of Rellouse Messenger",
            is_active=True,
            is_bot=False
        )
        
        db.add(owner)
        
        # Create @Verify system bot as a User
        verify_bot = User(
            id=1,
            login="verify_bot",
            password_hash=None,  # Bots don't need passwords
            username="@Verify",
            display_name="Verify Bot",
            bio="Official verification bot. Submit your verification request to get the verified badge.",
            is_active=True,
            is_bot=True,
            role=UserRole.ADMINISTRATOR
        )
        
        db.add(verify_bot)
        
        await db.commit()
        
        # Reset the auto-increment sequence to start from 2
        # This prevents conflicts with manually assigned IDs (0 and 1)
        await db.execute("SELECT setval('users_id_seq', 2, false)")
        await db.commit()
        
        logger.info(f"✅ Owner account created: @{settings.OWNER_USERNAME} (ID: 0)")
        logger.info(f"✅ @Verify bot created as User (ID: 1)")
        logger.info("✅ Auto-increment sequence reset to start from ID: 2")
        logger.info("✅ System initialization completed successfully")
        
        return True
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ System initialization failed: {str(e)}")
        raise


async def check_and_initialize(db: AsyncSession):
    """Check if system needs initialization and perform it"""
    try:
        await initialize_system(db)
    except Exception as e:
        logger.error(f"Failed to initialize system: {str(e)}")
        raise