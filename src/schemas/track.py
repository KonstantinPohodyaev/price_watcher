from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.database.annotations import not_null_str
from src.database.enums import Marketplace
from src.models.track import IMAGE_URL_MAX_LENGTH, URL_MAX_LENGTH
from src.schemas.user import ShortUserRead

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

DECIMAL_ZERO = '0.00'
DECIMAL_QUANTIZE = '0.00'
DECIMAL_PLACES = 2


class TargetAndCurrentPriceFields(BaseModel):
    """Схема для добавления полей target_price и current_price."""

    target_price: Optional[Decimal] = Field(
        None, decimal_places=DECIMAL_PLACES
    )
    current_price: Optional[Decimal] = Field(
        None, decimal_places=DECIMAL_PLACES
    )

    @field_validator('target_price', 'current_price', mode='before')
    @classmethod
    def format_decimal_fields(cls, value: Decimal) -> str:
        """Валидатор для Decimal-полей."""
        try:
            decimal_value = Decimal(str(value))
            if 'E' in str(value).upper():
                return Decimal(DECIMAL_ZERO)
            return decimal_value.quantize(
                Decimal(DECIMAL_QUANTIZE), rounding=ROUND_HALF_UP
            )
        except Exception:
            return Decimal(DECIMAL_ZERO)


class BaseTrack(TargetAndCurrentPriceFields):
    """Базовая схема для модели PriceHistory."""
    marketplace: Optional[Marketplace] = Field(None)
    article: Optional[str] = Field(None)
    title: Optional[str] = Field(None)
    image_url: Optional[str] = Field(
        None, max_length=IMAGE_URL_MAX_LENGTH
    )
    last_checked_at: Optional[datetime] = Field(None)
    is_active: Optional[bool] = Field(None)

    class Config:
        title = BASE_TRACK_TITLE


class TrackDB(BaseTrack):
    """Схема для отображения PriceHistory в БД."""
    id: Optional[int]
    user: ShortUserRead
    created_at: datetime

    class Config:
        title = TRACK_DB_TITLE
        from_attributes = True


class TrackUserDataCreate(BaseModel):
    """Pydantic-схема для создания экземпляра Track в БД."""

    marketplace: Marketplace
    article: str
    target_price: Decimal

    class Config:
        title = TRACK_CREATE_TITLE


class TrackDBCreate(BaseTrack):
    user_id: Optional[int] = Field(None)


class TrackUpdate(BaseTrack):
    """Pydantic-схема для обновления экземпляра Track в БД."""

    class Config:
        title = TRACK_UPDATE_TITLE


class TrackFilterSchema(BaseModel):
    marketplace: Optional[Marketplace]
    is_active: Optional[bool]
    user_id: Optional[int]
