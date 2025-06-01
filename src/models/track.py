from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk, not_null_decimal, not_null_str
from src.database.enums import Marketplace
from src.models.base import Base

if TYPE_CHECKING:
    from src.models.price_history import PriceHistory
    from src.models.user import User


URL_MAX_LENGTH = 2 ** 11
IMAGE_URL_MAX_LENGTH = 2 ** 11


class Track(Base):
    """Модель для отслеживаемого url."""

    id: Mapped[int_pk]
    marketplace: Mapped[Marketplace] = mapped_column(
        nullable=False
    )
    article: Mapped[not_null_str]
    title: Mapped[not_null_str]
    image_url: Mapped[str | None] = mapped_column(
        String(IMAGE_URL_MAX_LENGTH),
        nullable=True
    )
    target_price: Mapped[not_null_decimal]
    current_price: Mapped[not_null_decimal]
    last_checked_at: Mapped[datetime] = mapped_column(
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        default=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE')
    )
    user: Mapped['User'] = relationship(
        'User',
        back_populates='tracks',
        lazy='selectin',
    )
    price_history: Mapped[list['PriceHistory']] = relationship(
        'PriceHistory',
        back_populates='track',
        lazy='selectin'
    )
