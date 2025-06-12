from typing import Optional

from fastapi_users import schemas
from pydantic import BaseModel, Field

from src.schemas.jwt_auth import JWTRead, JWTTokenUpdate


class UserRead(schemas.BaseUser[int]):
    id: Optional[int]
    telegram_id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
    hashed_password: Optional[str]
    jwt_token: Optional[JWTRead]
    chat_id: Optional[str]

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    telegram_id: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    surname: Optional[str] = Field(None)
    chat_id: Optional[str] = Field(None)


class UserUpdate(schemas.BaseUserUpdate):
    telegram_id: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    surname: Optional[str] = Field(None)
    jwt_token: Optional[JWTTokenUpdate] = Field(None)


class ShortUserRead(BaseModel):
    """Укороченная схема пользователя."""
    id: int
    email: str
    name: Optional[str]
    surname: Optional[str]
    is_superuser: bool
    chat_id: Optional[str]
    jwt_token: Optional[JWTTokenUpdate] = Field(None)


class CheckTGID(BaseModel):
    telegram_id: int


class CheckEmail(BaseModel):
    email: str
