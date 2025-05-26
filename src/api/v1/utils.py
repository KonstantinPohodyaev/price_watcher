"""Модель для вспомогательных инструментов."""

from decimal import Decimal

import aiohttp

from src.schemas.track import TrackUserDataCreate, TrackDBCreate
from src.api.v1.constants import WILDBBERIES_PRODUCT_CARD_URL
from src.api.v1.validators import check_not_existent_article


async def wildberries_parse(create_track_schema: TrackUserDataCreate):
    """Получает информацию о товаре по его артикулу."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            WILDBBERIES_PRODUCT_CARD_URL.format(
                nm_id=create_track_schema.article
            )
        ) as response:
            data = await response.json()
            check_not_existent_article(create_track_schema.article, data)
            return data


def get_wildberries_product_data(
    create_track_schema: TrackDBCreate, product_data
) -> float:
    """Заполняет поля объекта Track по полученном товару."""
    
    create_track_schema.current_price = int(
        product_data['data']['products'][0]['salePriceU']
    ) / 100
    create_track_schema.title = product_data['data']['products'][0]['name']
    return create_track_schema
