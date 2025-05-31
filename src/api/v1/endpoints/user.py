from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from src.core.user import auth_backend, fastapi_users
from src.schemas.user import (
    UserCreate, UserRead, UserUpdate, CheckTGID
)
from src.database.db import get_async_session
from src.crud.user import user_crud
from src.models.user import User
from src.core.user import (
    current_superuser, current_user, get_user_db, UserManager,
    get_user_manager
)
from src.api.v1.validators import (
    check_user_exists_by_id, check_yourself_or_superuser
)


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
users_router = fastapi_users.get_users_router(
    UserRead,
    UserUpdate
)
users_router.routes = [
    rout for rout in users_router.routes if rout.name != 'users:delete_user'
]

@users_router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    id: int,
    current_user: User = Depends(current_user),
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
    user_manager: UserManager = Depends(get_user_manager)
):
    target_user = await check_user_exists_by_id(id, user_db)
    check_yourself_or_superuser(current_user, target_user)
    await user_manager.delete(target_user)



router.include_router(
    users_router,
    prefix=USER_PREFIX,
    tags=USER_TAGS
)

@service_router.post(
    '/check-telegram-id',
    response_model=UserRead | None,
    status_code=status.HTTP_200_OK
)
async def check_existence_user_by_telegram_id(
    telegram_id_schema: CheckTGID,
    session: AsyncSession = Depends(get_async_session)
):
    user = await user_crud.get_user_by_telegram_id(
        telegram_id_schema.telegram_id, session
    )
    return user if user else None


router.include_router(
    service_router,
    prefix=USER_PREFIX,
    tags=USER_TAGS
)
