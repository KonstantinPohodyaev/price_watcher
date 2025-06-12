import aiohttp
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.utils import WILDBBERIES_PRODUCT_CARD_URL
from src.core.user import current_user
from src.crud.price_history import price_history_crud
from src.crud.track import track_crud
from src.database.db import get_async_session
from src.models.user import User
from src.schemas.price_history import PriceHistoryCreate, PriceHistoryDB

MAX_TRACKS_PRICE_HISTORY_LEN = 3


router = APIRouter()


@router.get(
    '/price-history/{track_id}',
    response_model=list[PriceHistoryDB]
)
async def get_price_history_by_track_id(
    track_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Возвращает историю товара."""
    return await price_history_crud.get_history_by_track_id(track_id, session)


@router.post(
    '/price_history/{track_id}',
    response_model=PriceHistoryDB
)
async def add_entry_about_track(
    track_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Создает запись в истории товара."""
    track = await track_crud.get(track_id, session)
    if len(track.price_history) >= MAX_TRACKS_PRICE_HISTORY_LEN:
        await price_history_crud.delete_the_oldest_price_history(session)
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
