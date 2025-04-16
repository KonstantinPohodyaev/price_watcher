from typing import TYPE_CHECKING

from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.database.annotations import int_pk

if TYPE_CHECKING:
    from src.models.track import Track

class PriceHistory(Base):
    """История цен."""

    id: Mapped[int_pk]
    price: Mapped[Decimal] = mapped_column(
        nullable=False
    )
    track_id: Mapped[int] = mapped_column(
        ForeignKey('track.id')
    )
    track: Mapped['Track'] = relationship(
        'Track',
        back_populates='price_history',
        lazy='selectin'
    )
