from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.price_history import PriceHistoryDB
from src.database.db import get_async_session


router = APIRouter()


@router.get(
    '/price-history/{track_article}',
    response_model=list[PriceHistoryDB]
)
async def get_price_history_by_article(
    track_article: str,
    session: AsyncSession = Depends(get_async_session)
):
    