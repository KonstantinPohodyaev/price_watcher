from typing import Optional

from fastapi_users import schemas

from src.models.track import Track


class UserRead(schemas.BaseUser[int]):
    telegram_id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
    tracs: Optional[list[Track]]


class UserCreate(schemas.BaseUserCreate):
    telegram_id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
    tracs: Optional[list[Track]]


class UserUpdate(schemas.BaseUserUpdate):
    telegram_id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
    tracs: Optional[list[Track]]
