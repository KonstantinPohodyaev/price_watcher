import aiohttp
from telegram import Update
from telegram.ext import (
    ContextTypes, ApplicationBuilder, InlineQueryHandler, CallbackQueryHandler
)

from bot.handlers.utils import catch_error, escape_markdown_v2
from bot.handlers.pre_process import load_data_for_register_user
from bot.endpoints import GET_USERS_TRACKS
from bot.handlers.utils import check_authorization


SHOW_ALL_ERROR = (
    'Что-то пошло не так при загрузке отслеживаемых товаров! ❌\n'
    'Пробуйте еще раз!'
)
SHOW_ALL_AUTH_ERROR = (
    'Перед просмотром отслеживаемых товаров необходимо пройти '
    '/auth авторизацию ⚠️'
)
SHORT_TRACK_CARD = """
<b>{title}</b> - <code>{article}</code>
_________________________
Текущая цена: <b>{current_price}</b>
Желаемая цена: <b>{target_price}</b>
"""

@load_data_for_register_user
@catch_error(SHOW_ALL_ERROR)
async def show_all(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    if not await check_authorization(query, context):
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(
            GET_USERS_TRACKS,
            headers=dict(
            Authorization=(
                f'Bearer {context.user_data["account"]["jwt_token"]}'
            )
        )
        ) as response:
            tracks = await response.json()
            for track in tracks:
                await query.message.reply_text(
                    text=(SHORT_TRACK_CARD.format(
                        title=track.get('title'),
                        article=track.get('article'),
                        current_price=track.get('current_price'),
                        target_price=track.get('target_price')
                    )),
                    parse_mode='HTML'
                    
                )


def handlers_installer(
    application: ApplicationBuilder
) -> None:
    application.add_handler(
        CallbackQueryHandler(show_all, pattern='^track_show_all$')
    )
