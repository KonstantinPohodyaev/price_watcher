from fastapi import APIRouter

from src.core.user import auth_backend, fastapi_users
from src.schemas.user import UserCreate, UserRead, UserUpdate


router = APIRouter()

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