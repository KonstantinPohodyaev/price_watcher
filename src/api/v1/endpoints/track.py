from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.track import TrackDB, TrackCreate
from src.crud.track import track_crud
from src.database.db import get_async_session
from src.api.v1.validators import check_track_exists_by_id


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


@router.get(
    '/tracks/{track_id}',
    status_code=status.HTTP_200_OK,
    response_model=TrackDB
)
async def get_track_by_id(
    track_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> TrackDB:
    await check_track_exists_by_id(track_id, track_crud, session)
    return await track_crud.get(track_id, session)


@router.post(
    '/tracks',
    status_code=status.HTTP_201_CREATED,
    response_model=TrackDB
)
async def create_track(
    create_track_schema: TrackCreate,
    session: AsyncSession = Depends(get_async_session)
) -> TrackDB:
    