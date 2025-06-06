"""Модель для вспомогательных инструментов."""

from decimal import Decimal
from typing import Union

import aiohttp

from src.api.v1.constants import WILDBBERIES_PRODUCT_CARD_URL
from src.api.v1.validators import check_not_existent_article
from src.schemas.track import TrackDBCreate, TrackUpdate, TrackUserDataCreate


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
    
    track_schema.current_price = Decimal(str(
        int(
                product_data['data']['products'][0]['salePriceU']
            ) / 100
    ))
    track_schema.title = product_data['data']['products'][0]['name']
    return track_schema
