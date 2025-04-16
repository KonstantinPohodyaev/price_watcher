from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.database.annotations import not_null_str
from src.database.annotations import int_pk

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.price_history import PriceHistory


URL_MAX_LENGTH = 2 ** 11
IMAGE_URL_MAX_LENGTH = 2 ** 11


class Track(Base):
    """Модель для отслеживаемого url."""

    id: Mapped[int_pk]
    url: Mapped[str] = mapped_column(
        String(URL_MAX_LENGTH),
        nullable=False,
        unique=True
    )
    title: Mapped[not_null_str]
    image_url: Mapped[str | None] = mapped_column(
        String(IMAGE_URL_MAX_LENGTH),
        nullable=True
    )
    target_price: Mapped[Decimal] = mapped_column(
        nullable=False
    )
    current_price: Mapped[Decimal] = mapped_column(
        nullable=False
    )
    last_checked_at: Mapped[datetime] = mapped_column(
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        default=True
    )
    users: Mapped[list['User']] = relationship(
        'User',
        back_populates='tracks',
        lazy='selectin',
        secondary='usertrack',
    )
    price_history: Mapped[list['PriceHistory']] = relationship(
        'PriceHistory',
        back_populates='track',
        lazy='selectin'
    )
