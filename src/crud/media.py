from src.crud.base import CRUDBase
from src.models.media import Media
from src.schemas.media import MediaCreate, MediaUpdate


class MediaCRUD(CRUDBase[Media, MediaCreate, MediaUpdate]):
    """CRUD-класс для модели Media."""
