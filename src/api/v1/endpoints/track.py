from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.track import TrackDB
from src.crud.track import track_crud
from src.database.db import get_async_session


router = APIRouter()


@router.get(
    '/tracks',
    status_code=status.HTTP_200_OK,
    response_model=list[TrackDB]
)
async def get_tracks(
    session: AsyncSession = Depends(get_async_session)
) -> list[TrackDB]:
    """Возвращает все объекты Track."""
    return await track_crud.get_multy(session)
