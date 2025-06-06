import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          ContextTypes, ConversationHandler,
                          InlineQueryHandler, MessageHandler)

from bot.endpoints import USERS_TRACKS, USERS_TRACKS_BY_ID
from bot.handlers.constants import MESSAGE_HANDLERS, PARSE_MODE
from bot.handlers.pre_process import load_data_for_register_user
from bot.handlers.utils import catch_error, check_authorization
from bot.handlers.validators import validate_price

SHOW_ALL_ERROR = (
    'Что-то пошло не так при загрузке отслеживаемых товаров! ❌\n'
    'Попробуйте еще раз!'
)
SHOW_ALL_AUTH_ERROR = (
    'Перед просмотром отслеживаемых товаров необходимо пройти '
    '/auth авторизацию ⚠️'
)
TRACK_REFRESH_ERROR = (
    'Что-то пошло не так при обновлении отслеживаемого товара! ❌\n'
    'Попробуйте еще раз!'
)
SHORT_TRACK_CARD = """
<b>{title}</b> - <code>{article}</code>
_________________________
Текущая цена: <b>{current_price}</b>
Желаемая цена: <b>{target_price}</b>
"""

NEW_TARGET_PRICE_MESSAGE = 'Укажите новую желаемую цену 🏷️'

TRACK_BUTTONS = [
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
            USERS_TRACKS,
            headers=dict(
            Authorization=(
                f'Bearer {context.user_data["account"]["jwt_token"]}'
            )
        )
        ) as response:
            tracks = await response.json()
            for track in tracks:
                TRACK_BUTTONS = [
                    [
                        InlineKeyboardButton(
                            'Изменить ⚡',
                            callback_data=f'track_target_price_refresh_{track["id"]}'
                        ),
                        InlineKeyboardButton(
                            'Удалить ❌',
                            callback_data=f'track_delete_{track["id"]}'
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            'Посмотреть историю 🛍️',
                            callback_data=f'track_check_history_{track["id"]}'
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
                    reply_markup=InlineKeyboardMarkup(TRACK_BUTTONS)
                )


async def get_new_target_price(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    context.user_data['track_id'] = query.data.split('_')[-1]
    if not await check_authorization(query, context):
        return ConversationHandler.END
    await query.message.reply_text(NEW_TARGET_PRICE_MESSAGE)
    return 'refresh_target_price'


@catch_error(TRACK_REFRESH_ERROR)
async def target_price_refresh(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    get_new_target_price = update.message.text
    validated_price = await validate_price(
        update, context, get_new_target_price
    )
    if not validated_price:
        return 'refresh_target_price'
    async with aiohttp.ClientSession() as session:
        refresh_data = dict(
            target_price=validated_price
        )
        async with session.patch(
            USERS_TRACKS_BY_ID.format(id=context.user_data['track_id']),
            headers=dict(
                Authorization=(
                    f'Bearer {context.user_data["account"]["jwt_token"]}'
                )
            ),
            json=refresh_data
        ) as response:
            await update.message.reply_text(
                'Цена успешно обновлена! ✅'
            )
            return ConversationHandler.END


def handlers_installer(
    application: ApplicationBuilder
) -> None:
    application.add_handler(
        CallbackQueryHandler(show_all, pattern='^track_show_all$')
    )
    refresh_target_price_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                get_new_target_price, pattern='^track_target_price_refresh_'
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
