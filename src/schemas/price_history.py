from datetime import datetime
from decimal import Decimal
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

TITLE_PRICE = 'Цена'
BASE_PRICE_HISTORY_TITLE = (
    'Базовый класс Pydantic-схемы для модели PriceHistory'
)

PRICE_HISTORY_DB = (
    'Pydantic-схема для отображения PriceHistory в БД.'
)
TITLE_TRACK_ID = 'ID товара'

DECIMAL_ZERO = '0.00'
DECIMAL_QUANTIZE = '0.00'
DECIMAL_PLACES = 2


class BasePriceHistory(BaseModel):
    """Базовая схема для модели PriceHistory."""
    id: Optional[int]
    price: Decimal = Field(
        None,
        title=TITLE_PRICE
    )
    track_id: int = Field(
        None,
        title=TITLE_TRACK_ID
    )

    target_price: Optional[Decimal] = Field(
        None, decimal_places=DECIMAL_PLACES
    )
    current_price: Optional[Decimal] = Field(
        None, decimal_places=DECIMAL_PLACES
    )

    @field_validator('price', mode='before')
    @classmethod
    def format_decimal_fields(cls, value: Decimal) -> str:
        """Валидатор для Decimal-поля."""
        try:
            decimal_value = Decimal(str(value))
            if 'E' in str(value).upper():
                return Decimal(DECIMAL_ZERO)
            return decimal_value.quantize(
                Decimal(DECIMAL_QUANTIZE), rounding=ROUND_HALF_UP
            )
        except Exception:
            return Decimal(DECIMAL_ZERO)

    class Config:
        title = BASE_PRICE_HISTORY_TITLE


class PriceHistoryDB(BasePriceHistory):
    """Схема для отображения PriceHistory в БД."""
    created_at: datetime

    class Config:
        title = PRICE_HISTORY_DB


class PriceHistoryCreate(BaseModel):
    """Схема для создания записи в истории."""

    price: Decimal
    track_id: int


class PriceHistoryUpdate(BasePriceHistory):
    """Схема для обновления записи истории."""
