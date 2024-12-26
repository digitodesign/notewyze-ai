from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy import event
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Get database URL from settings and convert to async URL
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine with proper pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # Enable connection health checks
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Create declarative base
Base = declarative_base()

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session with automatic cleanup."""
    session = async_session_factory()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        await session.rollback()
        raise
    finally:
        await session.close()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for getting database session."""
    async with get_session() as session:
        yield session

# Database event listeners
@event.listens_for(engine.sync_engine, "connect")
def connect(dbapi_connection, connection_record):
    """Log when a connection is created."""
    logger.info("Database connection established")

@event.listens_for(engine.sync_engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    """Log when a connection is checked out from the pool."""
    logger.debug("Database connection retrieved from pool")

@event.listens_for(engine.sync_engine, "checkin")
def checkin(dbapi_connection, connection_record):
    """Log when a connection is returned to the pool."""
    logger.debug("Database connection returned to pool")
