from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.validators import (
    check_track_exists_by_id, check_unique_track_by_marketplace_article
)
from src.api.v1.utils import wildberries_parse, get_wildberries_product_data
from src.crud.track import track_crud
from src.database.db import get_async_session
from src.database.enums import Marketplace
from src.schemas.track import (TrackUserDataCreate, TrackDB, TrackFilterSchema,
                               TrackUpdate, TrackDBCreate)
from src.schemas.price_history import PriceHistoryCreate
from src.crud.price_history import price_history_crud
from src.core.user import current_user
from src.models.user import User

router = APIRouter()


@router.get(
    '/tracks',
    status_code=status.HTTP_200_OK,
    response_model=list[TrackDB],
    response_model_exclude_none=True
)
async def get_users_tracks(
    is_active: bool = Query(None),
    marketplace: Marketplace = Query(None),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
) -> list[TrackDB]:
    filter_schema = TrackFilterSchema(
        marketplace=marketplace,
        is_active=is_active,
        user_id=user.id
    )
    """Возвращает все объекты Track."""
    return await track_crud.get_all(filter_schema, session)


@router.get(
    '/tracks/{track_id}',
    status_code=status.HTTP_200_OK,
    response_model=TrackDB,
    response_model_exclude_none=True
)
async def get_track_by_id(
    track_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> TrackDB:
    """Получает конкретный объект Track по его id."""
    await check_track_exists_by_id(track_id, track_crud, session)
    return await track_crud.get(track_id, session)


@router.post(
    '/tracks',
    status_code=status.HTTP_201_CREATED,
    response_model=TrackDB
)
async def create_track(
    create_track_schema: TrackUserDataCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Создает новый объект Track."""
    await check_unique_track_by_marketplace_article(
        create_track_schema.marketplace,
        create_track_schema.article,
        user.id,
        session
    )
    track_db_create_schema = TrackDBCreate(
        user_id=user.id, **create_track_schema.model_dump()
    )
    parsed_data = await wildberries_parse(
        track_db_create_schema
    )
    create_track_schema = get_wildberries_product_data(
        track_db_create_schema, parsed_data
    )
    new_track = await track_crud.create(
        track_db_create_schema, session
    )
    await price_history_crud.create(
        PriceHistoryCreate(
            price=new_track.current_price,
            track_id=new_track.id
        ),
        session
    )
    return new_track


@router.patch(
    '/tracks/{track_id}',
    status_code=status.HTTP_200_OK,
    response_model=TrackDB
)
async def update_track(
    track_id: int,
    update_track_schema: TrackUpdate,
    session: AsyncSession = Depends(get_async_session)
) -> TrackDB:
    """Частично обновляет существующий объект Track по id."""
    await check_track_exists_by_id(track_id, track_crud, session)
    return await track_crud.update(
        await track_crud.get(track_id, session),
        update_track_schema,
        session
    )


@router.delete(
    '/tracks/{track_id}',
    status_code=status.HTTP_200_OK,
    response_model=TrackDB
)
async def delete_track(
    track_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> TrackDB:
    await check_track_exists_by_id(track_id, track_crud, session)
    return await track_crud.delete(
        await track_crud.get(track_id, session), session
    )
