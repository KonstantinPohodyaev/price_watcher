from typing import Optional

from pydantic import BaseModel, Field


MEDIA_BASE_TITLE = 'Базовая Pydantic-схема для модели Media.'
MEDIA_DB_TITLE = 'Pydantic-схема для отображения объекта Media.'
MEDIA_CREATE_TITLE = 'Pydantic-схема для создания объекта Media.'
MEDIA_UPDATE_TITLE = 'Pydantic-схема для обновления объекта Media.'


class MediaBase(BaseModel):
    """Базовая Pydantic-схема для модели Media."""
    user_id: Optional[int] = Field(None)
    filename: Optional[str] = Field(None)
    url: Optional[str] = Field(None)
    path: Optional[str] = Field(None)

    class Config:
        """Класс настроек."""

        title = MEDIA_BASE_TITLE


class MediaDB(MediaBase):
    """Pydantic-схема для отображения объекта Media."""

    id: int

    class Config:
        """Класс настроек."""

        title = MEDIA_DB_TITLE
        from_attributes = True


class MediaCreate(BaseModel):
    """Pydantic-схема для создания объекта Media."""
    user_id: int
    filename: str
    url: str
    path: str

    class Config:
        """Класс настроек."""

        title = MEDIA_CREATE_TITLE


class MediaUpdate(MediaBase):
    """Pydantic-схема для обновления объекта Media."""

    class Config:
        """Класс настроек."""

        title = MEDIA_UPDATE_TITLE
