from typing import Optional

from fastapi_users import schemas
from pydantic import Field, BaseModel

from src.schemas.jwt_auth import JWTRead


class UserRead(schemas.BaseUser[int]):
    id: Optional[int]
    telegram_id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
    hashed_password: Optional[str]
    # jwt_token: Optional[JWTRead]


class UserCreate(schemas.BaseUserCreate):
    telegram_id: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    surname: Optional[str] = Field(None)


class UserUpdate(schemas.BaseUserUpdate):
    telegram_id: Optional[int]
    name: Optional[str]
    surname: Optional[str]


class ShortUserRead(BaseModel):
    """Укороченная схема пользователя."""
    id: int
    email: str
    name: Optional[str]
    surname: Optional[str]
    is_superuser: bool


class CheckTGID(BaseModel):
    telegram_id: int
