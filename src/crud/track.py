"""Модуль с инициализацией CRUD-класса для модели Track."""

from src.crud.base import CRUDBase
from src.models.track import Track
from src.schemas.track import TrackCreate, TrackUpdate


class TrackCRUD(CRUDBase[Track, TrackCreate, TrackUpdate]): ...


track_crud = TrackCRUD(Track)
