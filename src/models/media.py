from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk
from src.models.base import Base

if TYPE_CHECKING:
    from src.models.user import User


MEDIA_URL_MAX_LENGTH = 2 ** 11


class Media(Base):
    """Модель для хранения медиа."""

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE')
    )
    user: Mapped['User'] = relationship(
        'User',
        back_populates='media',
        lazy='selectin'
    )
    filename: Mapped[str] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(
        String(MEDIA_URL_MAX_LENGTH), nullable=False
    )
