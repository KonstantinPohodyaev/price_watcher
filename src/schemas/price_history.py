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


class BasePriceHistory(BaseModel):
    """Базовая схема для модели PriceHistory."""
    id: Optional[int]
    price: Decimal = Field(
        None,
        title=TITLE_PRICE
    )

    class Config:
        title = BASE_PRICE_HISTORY_TITLE


class PriceHistoryDB(BasePriceHistory):
    """Схема для отображения PriceHistory в БД."""

    class Config:
        title = PRICE_HISTORY_DB
