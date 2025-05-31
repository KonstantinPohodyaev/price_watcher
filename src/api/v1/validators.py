from decimal import Decimal

from fastapi import HTTPException, status
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.models.track import Track
from src.models.user import User


TRACK_NOT_EXISTS_BY_ID_ERROR = 'Товара с id = {id} не существует!'
USER_NOT_EXISTS_BY_ID_ERROR = 'Пользователя с id = {id} не существует!'
NOT_UNIQUE_TRACK_BY_MARKETPLACE_AND_ARTICLE = (
    'Товар с маркетплэйсом {marketplace} и артикулом {article} '
    'уже был добален пользователем {email}.'
)
CHECK_YOURSELF_OR_SUPERUSER_ERROR = (
    'Операция доступна только создателю аккаунта или супер-пользователю!'
)
NOT_EXISTENT_ARTICLE_ERROR = 'Товара с артикулом {article} не существует!'
NOT_NEGATIVE_TARGET_PRICE_ERROR = (
    'Желаемая цена не может быть отрицательной! '
    'Вы ввели: {target_price}'
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


def not_negative_target_price(target_price: Decimal) -> None:
    """Проверяет желаемую цену."""
    if target_price < Decimal('0'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=NOT_NEGATIVE_TARGET_PRICE_ERROR.format(
                target_price=target_price
            )
        )


async def check_track_exists_by_id(
    track_id: int,
    track_crud,
    session: AsyncSession
) -> None:
    """Проверяет существование объекта Track по его id."""
    await check_object_exists_by_id(
        track_id,
        track_crud,
        TRACK_NOT_EXISTS_BY_ID_ERROR,
        session
    )


async def check_user_exists_by_id(
    user_id: int,
    user_db: SQLAlchemyUserDatabase
) -> User:
    """Проверяет существование объекта User по его id."""
    user = await user_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=USER_NOT_EXISTS_BY_ID_ERROR.format(id=user_id)
        )
    return user


def check_yourself_or_superuser(
    current_user: User,
    target_user: User
) -> None:
    if current_user.id != target_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=CHECK_YOURSELF_OR_SUPERUSER_ERROR
        )


async def check_unique_track_by_marketplace_article(
    marketplace: str,
    article: str,
    user_id: int,
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


def check_not_existent_article(article: str, data: dict) -> None:
    """Проверяет существование артикула товара."""
    if not data['data']['products']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=NOT_EXISTENT_ARTICLE_ERROR.format(
                article=article
            )
        )
