from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    telegram_id: Optional[int]
    name: Optional[str]
    surname: Optional[str]


class UserCreate(schemas.BaseUserCreate):
    telegram_id: Optional[int]
    name: Optional[str]
    surname: Optional[str]


class UserUpdate(schemas.BaseUserUpdate):
    telegram_id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
