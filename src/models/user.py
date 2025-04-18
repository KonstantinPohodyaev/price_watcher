from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.track import Track

NAME_MAX_LENGTH = 128
SURNAME_MAX_LENGTH = 128


class User(Base, SQLAlchemyBaseUserTableUUID):
    """Модель пользователя, расширенная от базовой FastAPI_Users.

    Дополнительные поля:
        telegram_id (int): telegram-id.
        name (str): имя.
        surname (str): фамилия.
        hashed_password (str): захэшированный пароль.
    """

    telegram_id: Mapped[int | None] = mapped_column(
        unique=True, nullable=True
    )
    name: Mapped[str | None] = mapped_column(
        String(NAME_MAX_LENGTH), nullable=True
    )
    surname: Mapped[str | None] = mapped_column(
        String(SURNAME_MAX_LENGTH), nullable=True
    )
    hashed_password: Mapped[str] = mapped_column(
        nullable=False
    )
    tracks: Mapped[list['Track']] = relationship(
        'Track',
        secondary='usertrack',
        back_populates='users',
        lazy='selectin',
        cascade='all, delete-orphan'
    )
