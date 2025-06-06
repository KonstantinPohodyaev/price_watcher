import os

from cryptography.fernet import Fernet
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.jwt_auth import JWTToken
from src.schemas.jwt_auth import JWTTokenCreate, JWTTokenUpdate

fernet = Fernet(
    os.getenv(
        'JWT_SECRET_KEY',
        'A8zOVVp4FMb93RD03n0O25FwAYmTxmTQhF3kPBnLJ6E='
    )
)


class JWTCRUD:
    def __init__(self, model: JWTToken) -> None:
        """Инициализирует CRUD-класс для модели JWTToken."""
        self.model = model

    async def create(
        self,
        create_schema: JWTTokenCreate,
        session: AsyncSession,
        commit_on: bool = True
    ):
        encoded_access_token = fernet.encrypt(
            create_schema.access_token.encode()
        )
        create_schema.access_token = encoded_access_token
        new_encoded_jwt_token = JWTToken(
            **create_schema.model_dump()
        )
        try:
            session.add(new_encoded_jwt_token)
            if commit_on:
                await session.commit()
                await session.refresh(new_encoded_jwt_token)
            return new_encoded_jwt_token
        except IntegrityError as error:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Ошибка в данных токена'
            )
        except SQLAlchemyError as error:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Ошибка сервера при создании токена'
            )

    async def update(
        self,
        current_jwt_token: JWTToken,
        update_schema: JWTTokenUpdate,
        session: AsyncSession,
        commit_on: bool = True
    ):
        """Обновляет данные JWT-токена."""
        update_data = update_schema.model_dump(exclude_unset=True)
        if update_data.get('access_token'):
            new_encoded_access_token = fernet.encrypt(
                update_data.get('access_token').encode()
            )
            update_data['access_token'] = new_encoded_access_token
        for field, value in update_data.items():
            if field in update_data:
                setattr(current_jwt_token, field, value)
        try:
            session.add(current_jwt_token)
            if commit_on:
                await session.commit()
                await session.refresh(current_jwt_token)
            return current_jwt_token
        except IntegrityError as error:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Ошибка в данных токена'
            )
        except SQLAlchemyError as error:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Ошибка сервера при обновлении токена'
            )

    async def get_jwt_token_by_user_id(
        self,
        user_id: int,
        session: AsyncSession
    ):
        """Возвращает объект JWTToken по user_id."""
        return (
            await session.execute(
                select(JWTToken).where(
                    JWTToken.user_id == user_id
                )
            )
        ).scalar()


jwt_token_crud = JWTCRUD(JWTToken)
