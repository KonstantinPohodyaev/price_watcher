from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.models.track import Track

TRACK_NOT_EXISTS_BY_ID_ERROR = 'Товара с id = {id} не существует!'
NOT_UNIQUE_TRACK_BY_MARKETPLACE_AND_ARTICLE = (
    'Товар с маркетплэйсом {marketplace} и артикулом {article} '
    'уже был добален пользователем {email}.'
)


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


async def check_unique_track_by_marketplace_article(
    marketplace: str,
    article: str,
    user_id: UUID,
    session: AsyncSession
) -> None:
    """Проверяет, нет ли у пользователя уже такого товара в базе."""
    result = await session.execute(
        select(Track).where(
            and_(
                Track.marketplace == marketplace,
                Track.article == article,
                Track.user_id == user_id
            )
        )
    )

    if result.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=NOT_UNIQUE_TRACK_BY_MARKETPLACE_AND_ARTICLE.format(
                marketplace=marketplace,
                article=article,
                email=user_id
            )
        )
