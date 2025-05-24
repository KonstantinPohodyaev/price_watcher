from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.price_history import PriceHistory
from src.schemas.price_history import (
    PriceHistoryCreate, PriceHistoryUpdate
)
from src.crud.base import CRUDBase


class PriceHisstoryCRUD(
    CRUDBase[PriceHistory, PriceHistoryCreate, PriceHistoryUpdate]
):
    async def get_history_by_track_id(
        self,
        track_id: int,
        session: AsyncSession
    ):
        result =  await session.execute(
            select(self.model).where(self.model.track_id == track_id)
        )
        return result.scalars().all()


price_history_crud = PriceHisstoryCRUD(PriceHistory)
