"""
Update Owner Password Script
Updates the owner account password in the database
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from models import User
from security import password_hasher
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_owner_password():
    """Update the owner account password"""
    try:
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True
        )
        
        # Create async session
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with async_session() as session:
            # Find owner account (ID: 0)
            result = await session.execute(
                select(User).where(User.id == 0)
            )
            owner = result.scalar_one_or_none()
            
            if not owner:
                logger.error("❌ Owner account not found (ID: 0)")
                return False
            
            logger.info(f"Found owner account: {owner.username} (ID: {owner.id})")
            
            # Hash new password
            new_password = settings.OWNER_PASSWORD
            new_password_hash = password_hasher.hash_password(new_password)
            
            # Update password
            owner.password_hash = new_password_hash
            
            await session.commit()
            
            logger.info(f"✅ Owner password updated successfully!")
            logger.info(f"   Username: {owner.username}")
            logger.info(f"   New Password: {new_password}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to update owner password: {str(e)}")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(update_owner_password())
