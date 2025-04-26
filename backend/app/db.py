from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URI),
    pool_pre_ping=True,
    echo=False  # Set to True for debugging SQL queries
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    class_=AsyncSession
)

# Create declarative base
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI endpoints to get a database session
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
