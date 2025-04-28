from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


TRACK_NOT_EXISTS_BY_ID_ERROR = 'Товара с id = {id} не существует!'


async def check_object_exists_by_id(
    object_id: int,
    object_crud,
    error_message: str,
    session: AsyncSession
) -> None:
    """Базовая функция для проверки существования объекта по id."""
    db_object = await object_crud.get(object_id, session)
    if not db_object:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message.format(id=object_id)
        )


async def check_track_exists_by_id(
    track_id: int,
    track_crud,
    session: AsyncSession
) -> None:
    await check_object_exists_by_id(
        track_id,
        track_crud,
        TRACK_NOT_EXISTS_BY_ID_ERROR,
        session
    )