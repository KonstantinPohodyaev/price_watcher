from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from sqlalchemy.exc import SQLAlchemyError

from src.models.price_history import PriceHistory
from src.schemas.price_history import (
    PriceHistoryCreate, PriceHistoryUpdate
)
from src.crud.base import CRUDBase


THE_OLDEST_DELETE_ERROR_MESSAGE = (
    'Ошибка при удалении самой старой записи в истории. '
    'Текст ошибки: {error_message}'
)


class PriceHistoryCRUD(
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

    async def delete_the_oldest_price_history(
        self,
        session: AsyncSession,
        commit_on: bool = True
    ):
        try:
            the_oldest_price_history = (
                await session.execute(
                    select(self.model).order_by(asc(self.model.created_at))
                )
            ).scalar()
            print('Самая старая запись: ', the_oldest_price_history)
            await session.delete(the_oldest_price_history)
            if commit_on:
                await session.commit()
            return the_oldest_price_history
        except SQLAlchemyError as error:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=THE_OLDEST_DELETE_ERROR_MESSAGE.format(
                    error_message=str(error)
                )
            )
                
       


price_history_crud = PriceHistoryCRUD(PriceHistory)
