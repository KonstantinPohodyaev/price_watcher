import aiohttp
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.price_history import PriceHistoryDB, PriceHistoryCreate
from src.database.db import get_async_session
from src.crud.price_history import price_history_crud
from src.crud.track import track_crud
from src.api.v1.utils import WILDBBERIES_PRODUCT_CARD_URL


router = APIRouter()


@router.get(
    '/price-history/{track_id}',
    response_model=list[PriceHistoryDB]
)
async def get_price_history_by_track_id(
    track_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    return await price_history_crud.get_history_by_track_id(track_id, session)


@router.post(
    '/price_history/{track_id}',
    response_model=PriceHistoryDB
)
async def add_entry_about_track(
    track_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    track = await track_crud.get(track_id, session)
    async with aiohttp.ClientSession() as local_session:
        async with local_session.get(
            WILDBBERIES_PRODUCT_CARD_URL.format(
                nm_id=track.article
            )
        ) as response:
            data = await response.json()
            price = data['data']['products'][0]['salePriceU'] / 100
            return await price_history_crud.create(
                PriceHistoryCreate(price=price, track_id=track_id),
                session
            )
