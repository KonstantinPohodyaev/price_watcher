from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

TITLE_PRICE = 'Цена'
BASE_PRICE_HISTORY_TITLE = (
    'Базовый класс Pydantic-схемы для модели PriceHistory'
)

PRICE_HISTORY_DB = (
    'Pydantic-схема для отображения PriceHistory в БД.'
)
TITLE_TRACK_ID = 'ID товара'


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

    class Config:
        title = BASE_PRICE_HISTORY_TITLE


class PriceHistoryDB(BasePriceHistory):
    """Схема для отображения PriceHistory в БД."""

    class Config:
        title = PRICE_HISTORY_DB


class PriceHistoryCreate(BaseModel):
    """Схема для создания записи в истории."""

    price: Decimal
    track_id: int


class PriceHistoryUpdate(BasePriceHistory):
    """Схема для обновления записи истории."""

    pass