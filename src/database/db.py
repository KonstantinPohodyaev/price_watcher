"""Файл с настройками БД."""

from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings


engine = create_async_engine(settings.database_url)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, Any]:
    """Генератор асинхронных сессий."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
