import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ApplicationBuilder, InlineQueryHandler,
    CallbackQueryHandler, ConversationHandler, MessageHandler
)

from bot.handlers.utils import catch_error
from bot.handlers.pre_process import load_data_for_register_user
from bot.endpoints import GET_USERS_TRACKS
from bot.handlers.utils import check_authorization
from bot.handlers.constants import PARSE_MODE, MESSAGE_HANDLERS


SHOW_ALL_ERROR = (
    'Что-то пошло не так при загрузке отслеживаемых товаров! ❌\n'
    'Пробуйте еще раз!'
)
SHOW_ALL_AUTH_ERROR = (
    'Перед просмотром отслеживаемых товаров необходимо пройти '
    '/auth авторизацию ⚠️'
)
TRACK_REFRESH_ERROR = (
    'Что-то пошло не так при обновлении отслеживаемого товара! ❌\n'
    'Пробуйте еще раз!'
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
                buttons = [
                    [
                        InlineKeyboardButton(
                            'Изменить ⚡',
                            callback_data='track_target_price_refresh'
                        ),
                        InlineKeyboardButton(
                            'Удалить ❌',
                            callback_data='track_delete'
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            'Посмотреть историю 🛍️',
                            callback_data='track_check_history'
                        )
                    ]
                ]
                await query.message.reply_text(
                    text=SHORT_TRACK_CARD.format(
                        title=track.get('title'),
                        article=track.get('article'),
                        current_price=track.get('current_price'),
                        target_price=track.get('target_price')
                    ),
                    parse_mode=PARSE_MODE,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )


async def get_new_target_price(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    if not await check_authorization(query, context):
        return
    await query.message.reply_text(
        'Укажите новую желаемую цену 🏷️'
    )
    return 


@catch_error(TRACK_REFRESH_ERROR)
async def target_price_refresh(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    if not await check_authorization(query, context):
        return
    get_new_target_price = query.message.text
    async with aiohttp.ClientSession() as session:
        pass

def handlers_installer(
    application: ApplicationBuilder
) -> None:
    application.add_handler(
        CallbackQueryHandler(show_all, pattern='^track_show_all$')
    )
    refresh_target_price_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                get_new_target_price, pattern='^track_target_price_refresh$'
            )
        ],
        states={
            'refresh_target_price': [
                MessageHandler(MESSAGE_HANDLERS, target_price_refresh)
            ]
        },
        fallbacks=[
            MessageHandler(MESSAGE_HANDLERS, target_price_refresh)
        ]
    )
    application.add_handler(
        refresh_target_price_conversation_handler
    )
