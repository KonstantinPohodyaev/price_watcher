import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          ContextTypes, ConversationHandler,
                          InlineQueryHandler, MessageHandler)

from bot.endpoints import USERS_TRACKS, USERS_TRACKS_BY_ID
from bot.handlers.constants import MESSAGE_HANDLERS, PARSE_MODE
from bot.handlers.pre_process import load_data_for_register_user
from bot.handlers.utils import (
    catch_error, check_authorization, get_interaction, get_headers
)
from bot.handlers.validators import validate_price
from bot.endpoints import CREATE_NEW_TRACK


SHOW_ALL_ERROR = (
    'Что-то пошло не так при загрузке отслеживаемых товаров! ❌\n'
    'Попробуйте еще раз!'
)
EMPTY_TRACKS = (
    'У вас пока нет отслеживаемых товаров 😢'
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

SELECT_MARKETPLACE_MESSAGE = 'Выберите маркетплэйс для поиска товара 🛍️'
SELECT_ARTICLE_MESSAGE = 'Укажите артикул товара 🏷️'
SELECT_TARGET_PRICE_MESSAGE = 'Укажите желаемую цену 🧾'
SUCCESS_CREATE_TRACK_MESSAGE = 'Новый товар добавлен! ✅'
CREATE_NEW_TRACK_ERROR = 'Ошибка при создании нового товара ⚠️'

TRACK_CARD = """
<b>{title}</b> - <code>{article}</code>
_________________________
Текущая цена: <b>{current_price}</b>
Желаемая цена: <b>{target_price}</b>
Дата создания: <b>{created_at}</b>
Дата последней проверки: <b>{last_checked_at}</b>
"""

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
            main_buttons = [
                [
                    InlineKeyboardButton(
                        'Отследить товар 🔍',
                        callback_data='track_add_track'
                    )
                ]
            ]
            tracks = await response.json()
            if not tracks:
                await query.message.reply_text(
                    EMPTY_TRACKS,
                    reply_markup=InlineKeyboardMarkup(main_buttons)
                )
                return
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
            await query.message.reply_text(
                'Навигация 💬',
                reply_markup=InlineKeyboardMarkup(main_buttons)
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


async def select_marketplace(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['new_track'] = dict()
    interaction = await get_interaction(update)
    buttons = [
        [
            InlineKeyboardButton('WB 🟣', callback_data='track_wildberries'),
            InlineKeyboardButton('OZON 🔵', callback_data='track_ozon')
        ]
    ]
    await interaction.message.reply_text(
        SELECT_MARKETPLACE_MESSAGE,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return 'add_article'


async def add_article(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    context.user_data['new_track']['marketplace'] = query.data.split('_')[-1]
    await query.message.reply_text(
        SELECT_ARTICLE_MESSAGE
    )
    return 'add_target_price'


async def add_target_price(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['new_track']['article'] = update.message.text
    await update.message.reply_text(
        SELECT_TARGET_PRICE_MESSAGE
    )
    return 'create_new_track'


@catch_error(CREATE_NEW_TRACK_ERROR)
async def create_new_track(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    print(context.user_data['new_track'])
    context.user_data['new_track']['target_price'] = update.message.text
    async with aiohttp.ClientSession() as session:
        async with session.post(
            CREATE_NEW_TRACK,
            headers=get_headers(context),
            json=context.user_data['new_track']
        ) as response:
            new_track = await response.json()
            print(new_track)
            await update.message.reply_text(
                SUCCESS_CREATE_TRACK_MESSAGE
            )
            await update.message.reply_text(
                text=TRACK_CARD.format(
                    title=new_track['title'],
                    article=new_track['article'],
                    current_price=new_track['current_price'],
                    target_price=new_track['target_price'],
                    created_at=new_track['created_at'],
                    last_checked_at=new_track['last_checked_at']
                ),
                parse_mode=PARSE_MODE
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
    add_track_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                select_marketplace, pattern='^track_add_track$'
            )
        ],
        states={
            'add_article': [
                CallbackQueryHandler(
                    add_article, pattern='^track_(wildberries|ozon)$'
                )
            ],
            'add_target_price': [
                MessageHandler(
                    MESSAGE_HANDLERS, add_target_price
                )
            ],
            'create_new_track': [
                MessageHandler(MESSAGE_HANDLERS, create_new_track)
            ]
        },
        fallbacks=[
            MessageHandler(MESSAGE_HANDLERS, create_new_track)
        ]
    )
    application.add_handler(
        refresh_target_price_conversation_handler
    )
    application.add_handler(
        add_track_conversation_handler
    )
