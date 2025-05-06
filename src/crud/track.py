"""Модуль с инициализацией CRUD-класса для модели Track."""

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.track import Track
from src.schemas.track import TrackDBCreate, TrackUpdate


class TrackCRUD(CRUDBase[Track, TrackDBCreate, TrackUpdate]):
    async def get_all(self, filter_schema, session: AsyncSession):
        query = select(self.model)
        filters = [self.model.user_id == filter_schema.user_id]
        if filter_schema.marketplace:
            filters.append(
                self.model.marketplace == filter_schema.marketplace
            )
        if filter_schema.is_active is not None:
            filters.append(
                self.model.is_active == filter_schema.is_active
            )
        if filters:
            query = query.where(and_(*filters))
        return (await session.execute(query)).scalars().all()


track_crud = TrackCRUD(Track)
