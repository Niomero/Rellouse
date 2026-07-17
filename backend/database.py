"""
Database Connection and Session Management
Handles database connection, session creation, and initialization
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from config import settings
from models import Base
import logging

logger = logging.getLogger(__name__)

# Create async engine
# Convert postgresql:// to postgresql+asyncpg:// for async support
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    poolclass=NullPool,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncSession:
    """
    Dependency for getting database session
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - drop and recreate all tables"""
    async with engine.begin() as conn:
        # Drop all tables first to ensure clean schema
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Dropped all existing tables")
        # Create all tables with current schema
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


async def close_db():
    """Close database connection"""
    await engine.dispose()
    logger.info("Database connection closed")
