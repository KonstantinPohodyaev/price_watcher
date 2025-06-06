from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.jwt_auth import JWTToken
    from src.models.track import Track

NAME_MAX_LENGTH = 128
SURNAME_MAX_LENGTH = 128
EMAIL_MAX_LENGTH = 256


class User(Base, SQLAlchemyBaseUserTable):
    """Модель пользователя, расширенная от базовой FastAPI_Users.

    Дополнительные поля:
        telegram_id (int): telegram-id.
        name (str): имя.
        surname (str): фамилия.
        hashed_password (str): захэшированный пароль.
    """

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
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
        back_populates='user',
        lazy='selectin',
        cascade="all, delete-orphan"
    )
    is_verified: Mapped[bool] = mapped_column(
        nullable=False, default=True
    )
    jwt_token: Mapped['JWTToken'] = relationship(
        'JWTToken',
        back_populates='user',
        uselist=False,
        lazy='selectin',
        cascade='all, delete-orphan'
    )
