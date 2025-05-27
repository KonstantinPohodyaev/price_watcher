from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.user import auth_backend, fastapi_users
from src.schemas.user import (
    UserCreate, UserRead, UserUpdate, CheckTGID, ShortUserRead
)
from src.database.db import get_async_session
from src.crud.user import user_crud

router = APIRouter()
service_router = APIRouter()

AUTHENTICATION_PREFIX = '/auth/jwt'
AUTHENTICATION_TAGS = ['auth']

REGISTRATION_PREFIX = '/auth'
REGISTRATION_TAGS = ['auth']

USER_PREFIX = '/users'
USER_TAGS = ['users']


router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=AUTHENTICATION_PREFIX,
    tags=AUTHENTICATION_TAGS
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=REGISTRATION_PREFIX,
    tags=REGISTRATION_TAGS
)
router.include_router(
    fastapi_users.get_users_router(
        UserRead, UserUpdate
    ),
    prefix=USER_PREFIX,
    tags=USER_TAGS
)

@service_router.post(
    '/check-telegram-id',
    response_model=bool | ShortUserRead,
    status_code=status.HTTP_200_OK
)
async def check_existence_user_by_telegram_id(
    telegram_id_schema: CheckTGID,
    session: AsyncSession = Depends(get_async_session)
):
    user = await user_crud.get_user_by_telegram_id(
        telegram_id_schema.telegram_id, session
    )
    return user if user else False

router.include_router(
    service_router,
    prefix=USER_PREFIX,
    tags=USER_TAGS
)
