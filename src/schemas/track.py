from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from src.database.annotations import not_null_str
from src.database.enums import Marketplace
from src.models.track import IMAGE_URL_MAX_LENGTH, URL_MAX_LENGTH


URL_TITLE = 'URL-адрес товара'
BASE_TRACK_TITLE = (
    'Базовый класс Pydantic-схемы для модели Track'
)

TRACK_DB_TITLE = (
    'Pydantic-схема для отображения Track в БД.'
)
TRACK_CREATE_TITLE = (
    'Pydantic-схема для создания экземпляра Track в БД.'
)
TRACK_UPDATE_TITLE = (
    'Pydantic-схема для обновления экземпляра Track в БД.'
)


class BaseTrack(BaseModel):
    """Базовая схема для модели PriceHistory."""
    marketplace: Marketplace = Field(...)
    url: str = Field(
        None,
        title=URL_TITLE,
        max_length=URL_MAX_LENGTH
    )
    title: Optional[not_null_str]
    image_url: str = Field(
        None, max_length=IMAGE_URL_MAX_LENGTH
    )
    target_price: Optional[Decimal]
    current_price: Optional[Decimal]
    last_checked_at: Optional[datetime]
    is_active: Optional[bool]

    class Config:
        title = BASE_TRACK_TITLE


class TrackDB(BaseTrack):
    """Схема для отображения PriceHistory в БД."""
    id: Optional[int]

    class Config:
        title = TRACK_DB_TITLE
        from_attributes = True


class TrackCreate(BaseTrack):
    """Pydantic-схема для создания экземпляра Track в БД."""

    marketplace: Marketplace
    url: str = Field(
        ...,
        title=URL_TITLE,
        max_length=URL_MAX_LENGTH
    )
    title: not_null_str
    image_url: str = Field(
        ..., max_length=IMAGE_URL_MAX_LENGTH
    )
    target_price: Decimal

    class Config:
        title = TRACK_CREATE_TITLE


class TrackUpdate(BaseTrack):
    """Pydantic-схема для обновления экземпляра Track в БД."""

    class Config:
        title = TRACK_UPDATE_TITLE


class TrackFilterSchema(BaseModel):
    marketplace: Optional[Marketplace]
    is_active: Optional[bool]
