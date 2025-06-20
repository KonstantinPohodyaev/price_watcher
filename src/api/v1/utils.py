"""Модель для вспомогательных инструментов."""

from decimal import Decimal
from typing import Union

import aiohttp
from fastapi import HTTPException, status

from src.api.v1.constants import WILDBBERIES_PRODUCT_CARD_URL
from src.api.v1.validators import check_not_existent_article
from src.schemas.track import TrackDBCreate, TrackUpdate

GET_WILDBERRIES_PRODUCT_DATA_ERROR = (
    'Ошибка при получении данных для товара {article}. '
    'Возможно товара нет в наличии!'
)


async def wildberries_parse(article: str) -> dict:
    """Получает информацию о товаре по его артикулу."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            WILDBBERIES_PRODUCT_CARD_URL.format(
                nm_id=article
            )
        ) as response:
            data = await response.json()
            check_not_existent_article(article, data)
            return data


def get_wildberries_product_data(
    track_schema: Union[TrackDBCreate, TrackUpdate], product_data
) -> Union[TrackDBCreate, TrackUpdate]:
    """Заполняет поля объекта Track по полученном товару."""
    print(product_data)
    try:
        track_schema.current_price = Decimal(str(
            int(
                    product_data['data']['products'][0].get('salePriceU')
                ) / 100
        ))
        track_schema.title = product_data['data']['products'][0]['name']
        return track_schema
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=GET_WILDBERRIES_PRODUCT_DATA_ERROR.format(
                article=track_schema.article
            )
        )
