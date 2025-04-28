from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs

from src.database.annotations import created_at, updated_at


class Base(AsyncAttrs, DeclarativeBase):
    """Базовая модель SQLAlchemy.

    Аргументы:
        AsyncAttrs (_type_): возможность использовать await.
        DeclarativeBase (_type_): для создания базовой модели.
    """

    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
