"""Модуль с базовыми классами CRUD-операций."""

from typing import Generic, TypeVar, Type, Optional

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base


ModelType = TypeVar('Modeltype', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый CRUD-класс."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализирует CRUD-класс с указанной моделью."""
        self.model = model

    async def get_multy(
        self, session: AsyncSession
    ) -> Optional[list[ModelType]]:
        """Возвращает все объекты модели."""
        return (
            await session.execute(select(self.model))
        ).scalars().all()

    async def get(
        self,
        object_id: int,
        session: AsyncSession
    ) -> Optional[ModelType]:
        """Получение объекта по id."""
        return (
            await session.execute(
                select(self.model).where(self.model.id == object_id)
            )
        ).scalar()
