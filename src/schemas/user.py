from typing import Optional
from uuid import UUID

from fastapi_users import schemas
from pydantic import Field, BaseModel


class UserRead(schemas.BaseUser[int]):
    id: Optional[UUID]
    telegram_id: Optional[int]
    name: Optional[str]
    surname: Optional[str]


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
    id: UUID
    email: str
    name: Optional[str]
    surname: Optional[str]
    is_superuser: bool
