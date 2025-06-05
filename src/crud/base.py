"""Модуль с базовыми классами CRUD-операций."""

from typing import Generic, Optional, Type, TypeVar

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base

CREATE_ERROR_MESSAGE = (
    'Ошибка в данных для создания объекта! Текст ошибки: {error}'
)
UPDATE_ERROR_MESSAGE = (
    'Ошибка в данных при обновлении объекта! Текст ошибки: {error}'
)
SERVER_ERROR_MESSAGE = (
    'Возникла ошибка сервера при создании объекта! Текст ошибки {error}'
)


ModelType = TypeVar('Modeltype', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый CRUD-класс."""

    def __init__(self, model: Type[ModelType]) -> None:
        """Инициализирует CRUD-класс с указанной моделью."""
        self.model = model

    async def get_all(
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

    async def create(
        self,
        create_schema: CreateSchemaType,
        session: AsyncSession,
        commit_on: bool = True
    ) -> ModelType:
        """Создает новый объект в БД."""
        db_object = self.model(**create_schema.model_dump())
        try:
            session.add(db_object)
            if commit_on:
                await session.commit()
                await session.refresh(db_object)
            return db_object
        except IntegrityError as error:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=CREATE_ERROR_MESSAGE.format(
                    error=str(error)
                )
            )
        except SQLAlchemyError as error:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=SERVER_ERROR_MESSAGE.format(
                    error=str(error)
                )
            )

    async def update(
        self,
        db_object: ModelType,
        update_schema: UpdateSchemaType,
        session: AsyncSession,
        commit_on: bool = True
    ) -> ModelType:
        """Обновляет существующий объект (частичное обновение)."""
        current_data = jsonable_encoder(db_object)
        update_data = update_schema.model_dump(exclude_unset=True)
        for field in current_data:
            if field in update_data:
                setattr(db_object, field, update_data[field])
        try:
            session.add(db_object)
            if commit_on:
                await session.commit()
                await session.refresh(db_object)
            return db_object
        except IntegrityError as error:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=UPDATE_ERROR_MESSAGE.format(error=str(error)),
            )
        except SQLAlchemyError as error:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=SERVER_ERROR_MESSAGE.format(
                    error=str(error)
                ),
            )

    async def delete(
        self,
        db_object: ModelType,
        session: AsyncSession,
        commit_on: bool = True
    ) -> ModelType:
        """Удаляет объект из БД."""
        try:
            await session.delete(db_object)
            if commit_on:
                await session.commit()
            return db_object
        except SQLAlchemyError as error:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=SERVER_ERROR_MESSAGE.format(
                    error=str(error)
                )
            )
