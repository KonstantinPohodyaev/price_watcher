import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions, models, schemas
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.manager import BaseUserManager
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.validators import (check_unique_jwt_token_exists_by_user_id,
                                   check_user_exists_by_id,
                                   check_yourself_or_superuser)
from src.core.user import (AUTH_BACKEND_NAME, UserManager, auth_backend,
                           current_superuser, current_user, fastapi_users,
                           get_user_db, get_user_manager)
from src.crud.jwt_auth import jwt_token_crud
from src.crud.user import user_crud
from src.database.db import get_async_session
from src.models.user import User
from src.schemas.jwt_auth import JWTTokenCreate, JWTTokenUpdate
from src.schemas.user import (CheckEmail, CheckTGID, UserCreate, UserRead,
                              UserUpdate)

router = APIRouter()
service_router = APIRouter()

AUTHENTICATION_PREFIX = '/auth/jwt'
AUTHENTICATION_TAGS = ['auth']

REGISTRATION_PREFIX = '/auth'
REGISTRATION_TAGS = ['auth']

USER_PREFIX = '/users'
USER_TAGS = ['users']


auth_router = fastapi_users.get_auth_router(auth_backend)
auth_router.routes = [
    rout for rout in auth_router.routes if rout.name != 'auth:jwt.login'
]

login_responses: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.LOGIN_BAD_CREDENTIALS: {
                        "summary": "Bad credentials or the user is inactive.",
                        "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                    },
                    ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                        "summary": "The user is not verified.",
                        "value": {"detail": ErrorCode.LOGIN_USER_NOT_VERIFIED},
                    },
                }
            }
        },
    },
    **auth_backend.transport.get_openapi_login_responses_success(),
}

requires_verification = True

@auth_router.post(
    "/login",
    name=f"auth:{AUTH_BACKEND_NAME}.login",
    responses=login_responses,
)
async def login(
    request: Request,
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    strategy: Strategy[models.UP, models.ID] = Depends(auth_backend.get_strategy),
    session: AsyncSession = Depends(get_async_session)
):
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )
    if requires_verification and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
        )
    response = await auth_backend.login(strategy, user)
    serialized_data = json.loads(response.body.decode())
    access_token = serialized_data.get('access_token')
    token_type = serialized_data.get('token_type')
    jwt_token_db = await check_unique_jwt_token_exists_by_user_id(
        user.id, session
    )
    if jwt_token_db:
        update_schema = JWTTokenUpdate(
            access_token=access_token,
            token_type=token_type
        )
        await jwt_token_crud.update(
            jwt_token_db,
            update_schema,
            session
        )
    else:
        create_jwt_token_schema = JWTTokenCreate(
            access_token=access_token,
            token_type=token_type,
            user_id=user.id
        )
        await jwt_token_crud.create(create_jwt_token_schema, session)
    await user_manager.on_after_login(user, request, response)
    return response

router.include_router(
    auth_router,
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
    rout for rout in users_router.routes if (
        rout.name != 'users:delete_user'
        and rout.name != 'users:patch_current_user'
    )
]


@users_router.delete(
    '/{id}',
    name='users:delete_user',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    id: int,
    current_user: User = Depends(current_user),
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
    user_manager: UserManager = Depends(get_user_manager),
):
    target_user = await check_user_exists_by_id(id, user_db)
    check_yourself_or_superuser(current_user, target_user)
    await user_manager.delete(target_user)


@users_router.patch(
    "/me/refresh",
    name='users:custom_patch_current_user',
    response_model=UserRead,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {
                                "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
                            },
                        },
                        ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                    "at least 3 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def update_me(
    request: Request,
    user_update: UserUpdate,
    user: User = Depends(current_user),
    user_manager: BaseUserManager = Depends(get_user_manager),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Кастомный эндпоинт обновления данных текущего пользователя.

    Добавлено обновление токена в базе.
    """
    try:
        current_jwt_token = await jwt_token_crud.get_jwt_token_by_user_id(
            user.id, session
        )
        user_update_dict = user_update.model_dump(exclude_unset=True)
        user_update_dict.pop('jwt_token', None)
        cleaned_user_update = UserUpdate(**user_update_dict)
        user = await user_manager.update(
            cleaned_user_update, user, safe=True, request=request
        )
        if user_update.jwt_token:
            await jwt_token_crud.update(
                current_jwt_token,
                user_update.jwt_token,
                session
            )
        return schemas.model_validate(UserRead, user)
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
        )


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
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_crud.get_user_by_telegram_id(
        telegram_id_schema.telegram_id, session
    )
    return user if user else None


@service_router.post(
    '/check-email',
    response_model=UserRead | None,
    status_code=status.HTTP_200_OK
)
async def check_existence_user_by_email(
    email_schema: CheckEmail,
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_crud.get_user_by_email(
        email_schema.email, session
    )
    return user if user else None


router.include_router(
    service_router,
    prefix=USER_PREFIX,
    tags=USER_TAGS
)
