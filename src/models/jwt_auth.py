from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.annotations import int_pk
from src.database.enums import TokenType
from src.models.base import Base

if TYPE_CHECKING:
    from src.models.user import User



class JWTToken(Base):
    """Класс для хранения зашифрованных JWT-токенов."""
    id: Mapped[int_pk]
    access_token: Mapped[str] = mapped_column(nullable=False, unique=True)
    token_type: Mapped[TokenType] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'),
        unique=True,
        nullable=False
    )
    user: Mapped['User'] = relationship(
        'User',
        back_populates='jwt_token',
        lazy='selectin'
    )

    def to_dict(self):
        """Сериализатор для модели."""
        return dict(
            id=self.id,
            access_token=self.access_token,
            token_type=self.token_type,
            user_id=self.user_id
        )
