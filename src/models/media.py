from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.database.annotations import int_pk

if TYPE_CHECKING:
    from src.models.user import User



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
