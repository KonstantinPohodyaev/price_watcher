from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk, not_null_decimal, not_null_str
from src.database.enums import Marketplace
from src.models.base import Base

if TYPE_CHECKING:
    from src.models.price_history import PriceHistory
    from src.models.user import User


URL_MAX_LENGTH = 2 ** 11
IMAGE_URL_MAX_LENGTH = 2 ** 11

UNIQUE_ARTICLE_MARKETPLACE_USER_ID_CONSTRAINT_NAME = (
    'unique_article_marketplace_user_id'
)


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
        nullable=True, default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(
        default=True
    )
    notified: Mapped[bool] = mapped_column(
        default=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            'user.id', ondelete='CASCADE'
        )
    )
    user: Mapped['User'] = relationship(
        'User',
        back_populates='tracks',
        lazy='selectin',
    )
    price_history: Mapped[list['PriceHistory']] = relationship(
        'PriceHistory',
        back_populates='track',
        lazy='selectin',
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            'article', 'marketplace', 'user_id',
            name=UNIQUE_ARTICLE_MARKETPLACE_USER_ID_CONSTRAINT_NAME
        ),
    )

    # def to_dict(self):
    #     """Сериализатор для модели."""
    #     return dict(
    #         id=self.id,
    #         marketplace=self.marketplace,
    #         article=self.article,
    #         title=self.title,
    #         target_price=self.target_price,
    #         current_price=self.current_price,
    #         last_checked_at=self.last_checked_at,
    #         is_active=self.is_active,
    #         notified=self.notified,
    #         user_id=self.user_id,
    #         is_active=self.is_active,
    #         notified=self.notified,
    #         user_id=self.user_id
    #     )
