from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from src.models.track import URL_MAX_LENGTH, IMAGE_URL_MAX_LENGTH
from src.database.annotations import not_null_str

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
    id: Optional[int]
    url: HttpUrl = Field(
        None,
        title=URL_TITLE,
        max_length=URL_MAX_LENGTH
    )
    title: Optional[not_null_str]
    image_url: HttpUrl = Field(
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

    class Config:
        title = TRACK_DB_TITLE


class TrackCreate(BaseTrack):
    """Pydantic-схема для создания экземпляра Track в БД."""

    url: HttpUrl = Field(
        ...,
        title=URL_TITLE,
        max_length=URL_MAX_LENGTH
    )
    title: not_null_str
    image_url: HttpUrl = Field(
        ..., max_length=IMAGE_URL_MAX_LENGTH
    )
    target_price: Decimal

    class Config:
        title = TRACK_CREATE_TITLE


class TrackUpdate(BaseTrack):
    """Pydantic-схема для обновления экземпляра Track в БД."""

    class Config:
        title = TRACK_UPDATE_TITLE
