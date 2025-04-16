from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class UserTrack(Base):
    """Связующая таблица между моделями User и Track."""

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'), primary_key=True
    )
    track_id: Mapped[int] = mapped_column(
        ForeignKey('track.id'), primary_key=True
    )
