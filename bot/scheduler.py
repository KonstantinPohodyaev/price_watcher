from decimal import Decimal
from http import HTTPStatus

import aiohttp
from telegram import Bot
from telegram.ext import ContextTypes

from bot.endpoints import (REFRESH_DATA_FOR_EXISTEN_TRACK, UPDATE_TRACK_BY_ID,
                           USERS_TRACKS, ADD_ENTRY_ABOUT_TRACK)
from bot.handlers.utils import decode_jwt_token, get_headers

SUCCESS_PRICE = (
    '🎉 Цена на товар {article} опустилась до нужной!'
)
PERIODIC_CHECK_INTERVAL = 3
PERIODIC_CHECK_FIRST = 1

TOKEN_LIFETIME_ERROR = (
    '⛔ Срок действия токена истёк. Авторизуйтесь снова.'
)
GETTING_DATA_ERROR = (
    '⛔ Ошибка получения данных: код ошибки {status_code}'
)


async def periodic_check(context: ContextTypes.DEFAULT_TYPE):
    await check_prices_and_notify_users(context)


async def check_prices_and_notify_users(
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Функция для оповещения пользователей о понижении цены до target_price.
    """
    data = context.job.data
    jwt_token = data.get('jwt_token')
    chat_id = data.get('chat_id')
    if not jwt_token:
        await context.bot.send_message(chat_id, '❌ Токен не найден.')
        context.job.schedule_removal()
        return
    async with aiohttp.ClientSession() as session:
        headers = dict(
            Authorization=f'Bearer {jwt_token}'
        )
        async with session.get(
            USERS_TRACKS,
            headers=headers
        ) as response:
            if response.status == HTTPStatus.UNAUTHORIZED:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=TOKEN_LIFETIME_ERROR
                )
                context.job.schedule_removal()
                return
            elif response.status != HTTPStatus.OK:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=GETTING_DATA_ERROR.format(
                        status_code=response.status
                    )
                )
                return
            tracks = await response.json()
            for track in tracks:
                async with session.patch(
                    REFRESH_DATA_FOR_EXISTEN_TRACK.format(id=track['id']),
                    headers=headers
                ) as updated_response:
                    if updated_response.status != HTTPStatus.OK:
                        continue
                    updated_track = await updated_response.json()
                if (
                    Decimal(updated_track['target_price'])
                    >= Decimal(updated_track['current_price'])
                    and updated_track['notified'] is False
                ):
                    update_data = dict(
                        notified=True
                    )
                    async with session.patch(
                        UPDATE_TRACK_BY_ID.format(
                            id=track['id']
                        ),
                        json=update_data,
                        headers=headers
                    ):
                        pass
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=SUCCESS_PRICE.format(
                            article=updated_track['article']
                        )
                    )
                print(1)
                async with session.post(
                    ADD_ENTRY_ABOUT_TRACK.format(
                        track_id=track['id']
                    ),
                    headers=headers
                ) as response:
                    print(response.status)
