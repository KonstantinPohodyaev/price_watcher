"""Модель для вспомогательных инструментов."""

from decimal import Decimal

import aiohttp

from src.schemas.track import TrackUserDataCreate, TrackDBCreate


WILDBBERIES_PRODUCT_CARD_URL = (
    'https://card.wb.ru/cards/v1/detail'
    '?appType=1&curr=rub&dest=-1257786&spp=30&nm={nm_id}'
)

async def wildberries_parse(create_track_schema: TrackUserDataCreate):
    """Получает информацию о товаре по его артикулу."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            WILDBBERIES_PRODUCT_CARD_URL.format(
                nm_id=create_track_schema.article
            )
        ) as response:
            data = await response.json()
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
