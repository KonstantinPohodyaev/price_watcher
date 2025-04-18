from typing import Optional, Union

from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager, FastAPIUsers, IntegerIDMixin, InvalidPasswordException
)
from fastapi_users.authentication import (
    AuthenticationBackend, BearerTransport, JWTStrategy
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.database.db import get_async_session
from src.models.user import User
from src.schemas.user import UserCreate


BEARER_TRANSPORT_TOKEN_URL = 'auth/jwt/login'
LIFETIME_SECONDS = 3600
AUTH_BACKEND_NAME = 'jwt'

MIN_PASSWORD_LENGTH = 3
PASSWORD_LENGTH_ERROR = 'Пароль должен быть длиннее {min_password_length}'
PASSWORD_DATA_ERROR = 'Пароль не должен содержать данных о пользователе!'


async def get_user_db(
    session: AsyncSession = Depends(get_async_session)
):
    yield SQLAlchemyUserDatabase(session, User)

bearer_transport = BearerTransport(
    tokenUrl=BEARER_TRANSPORT_TOKEN_URL
)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.secret, lifetime_seconds=LIFETIME_SECONDS
    )

auth_backend = AuthenticationBackend(
    name=AUTH_BACKEND_NAME,
    transport=bearer_transport,
    get_strategy=get_jwt_strategy
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User]
    ) -> None:
        if len(password) < 3:
            raise InvalidPasswordException(
                reason=PASSWORD_LENGTH_ERROR.format(
                    min_password_length=MIN_PASSWORD_LENGTH
                )
            )
        for user_field in [user.email, user.name, user.surname]:
            if user_field in password:
                raise InvalidPasswordException(
                    reason=PASSWORD_DATA_ERROR
                )


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)