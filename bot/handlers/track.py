from http import HTTPStatus

import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          ContextTypes, ConversationHandler, MessageHandler)

from bot.endpoints import (CREATE_NEW_TRACK, DELETE_TRACK_BY_ID,
                           GET_TRACKS_PRICE_HISTORY, USERS_TRACKS,
                           USERS_TRACKS_BY_ID)
from bot.handlers.callback_data import (ADD_TRACK, CHECK_HISTORY, MENU, OZON,
                                        SHOW_ALL_TRACK, WILDBERRIES)
from bot.handlers.constants import MESSAGE_HANDLERS, PARSE_MODE
from bot.handlers.pre_process import load_data_for_register_user
from bot.handlers.utils import (catch_error, check_authorization, get_headers,
                                get_interaction, get_track_keyboard)
from bot.handlers.validators import validate_price

# Состояния для ConversationHandler
TARGET_PRICE_REFRESH_TARGET_PRICE = 'refresh_target_price'

ADD_TRACK_ADD_ARTICLE = 'add_article'
ADD_TRACK_ADD_TARGET_PRICE = 'add_target_price'
ADD_TRACK_CREATE_NEW_TRACK = 'create_new_track'

FINISH_DELETE_TRACK = 'delete_track'
CONFIRM_DELETE = 'confirm'
CANCEL_DELETE = 'cancel'


# Сообщения для reply_text
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
PRICE_HISTORY_ERROR = (
    'Ошибка при загрузке истории товара! ❌'
)
CREATE_BAD_REQUEST_ERROR = """
{error_message}
Попробуйте указать данные для товара заново.
"""
OUTDATED_AUTHORIZATION_ERROR = """
Повторите авторизацию! /auth
Срок действия истек 😢
"""
SHORT_TRACK_CARD = """
<b>{title}</b> - <code>{article}</code>
_________________________
ID: <b>{id}</b>
Текущая цена: <b>{current_price}</b>
Желаемая цена: <b>{target_price}</b>
"""
PRICE_HISTORY_CARD = """
Цена: <b>{price}</b>
Дата создания: <b>{date} {time}</b>
"""


NEW_TARGET_PRICE_MESSAGE = 'Укажите новую желаемую цену 🏷️'

SELECT_MARKETPLACE_MESSAGE = 'Выберите маркетплэйс для поиска товара 🛍️'
SELECT_ARTICLE_MESSAGE = 'Укажите артикул товара 🏷️'
SELECT_TARGET_PRICE_MESSAGE = 'Укажите желаемую цену 🧾'
SUCCESS_CREATE_TRACK_MESSAGE = 'Новый товар добавлен! ✅'
CREATE_NEW_TRACK_ERROR = 'Ошибка при создании нового товара ⚠️'
DELETE_TRACK_ERROR = 'Ошибка при удалении товара из отслеживаемых ⚠️'

TRACK_CARD = """
<b>{title}</b> - <code>{article}</code>
_________________________
💸 Текущая цена: <b>{current_price}</b>
🎯 Желаемая цена: <b>{target_price}</b>
Дата создания: <b>{created_at}</b>
Дата последней проверки: <b>{last_checked_at}</b>
"""


@catch_error(SHOW_ALL_ERROR)
@load_data_for_register_user
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
            headers=get_headers(context)
        ) as response:
            if response.status == HTTPStatus.UNAUTHORIZED:
                await query.message.reply_text(
                    OUTDATED_AUTHORIZATION_ERROR
                )
                return
            main_buttons = [
                [
                    InlineKeyboardButton(
                        'Отследить товар 🔍',
                        callback_data=ADD_TRACK
                    )
                ],
                [
                    InlineKeyboardButton(
                        'Меню 🛍️',
                        callback_data=MENU
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
                await query.message.reply_text(
                    text=SHORT_TRACK_CARD.format(
                        title=track.get('title'),
                        id=track.get('id'),
                        article=track.get('article'),
                        current_price=track.get('current_price'),
                        target_price=track.get('target_price')
                    ),
                    parse_mode=PARSE_MODE,
                    reply_markup=InlineKeyboardMarkup(
                        get_track_keyboard(track["id"])
                    )
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
    return 'save_new_target_price'


@catch_error(TRACK_REFRESH_ERROR, conv=True)
@load_data_for_register_user
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
            headers=get_headers(context),
            json=refresh_data
        ):
            buttons = [
                [
                    InlineKeyboardButton(
                        'Вернуться назад ⬅️',
                        callback_data=f'{SHOW_ALL_TRACK}'
                    )
                ]
            ]
            await update.message.reply_text(
                'Цена успешно обновлена! ✅',
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return ConversationHandler.END


async def select_marketplace(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['new_track'] = dict()
    interaction = await get_interaction(update)
    buttons = [
        [
            InlineKeyboardButton(
                'WB 🟣',
                callback_data=f'track_{WILDBERRIES}'
            ),
            InlineKeyboardButton(
                'OZON (WB)🔵',
                callback_data=f'track_{WILDBERRIES}'
            )
        ]
    ]
    await interaction.message.reply_text(
        SELECT_MARKETPLACE_MESSAGE,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return ADD_TRACK_ADD_ARTICLE


async def add_article(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    context.user_data['new_track']['marketplace'] = query.data.split('_')[-1]
    await query.message.reply_text(
        SELECT_ARTICLE_MESSAGE
    )
    return ADD_TRACK_ADD_TARGET_PRICE


async def add_target_price(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['new_track']['article'] = update.message.text
    await update.message.reply_text(
        SELECT_TARGET_PRICE_MESSAGE
    )
    return ADD_TRACK_CREATE_NEW_TRACK


@catch_error(CREATE_NEW_TRACK_ERROR, conv=True)
@load_data_for_register_user
async def create_new_track(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['new_track']['target_price'] = update.message.text
    async with aiohttp.ClientSession() as session:
        async with session.post(
            CREATE_NEW_TRACK,
            headers=get_headers(context),
            json=context.user_data['new_track']
        ) as response:
            if response.status == HTTPStatus.UNAUTHORIZED:
                await update.message.reply_text(
                    OUTDATED_AUTHORIZATION_ERROR
                )
                return ConversationHandler.END
            elif response.status == HTTPStatus.BAD_REQUEST:
                error_data = await response.json()
                await update.message.reply_text(
                    CREATE_BAD_REQUEST_ERROR.format(
                        error_message=error_data.get('detail')
                    )
                )
                await select_marketplace(update, context)
                return ADD_TRACK_ADD_ARTICLE
            new_track = await response.json()
            await update.message.reply_text(SUCCESS_CREATE_TRACK_MESSAGE)
            await update.message.reply_text(
                text=TRACK_CARD.format(
                    title=new_track['title'],
                    article=new_track['article'],
                    current_price=new_track['current_price'],
                    target_price=new_track['target_price'],
                    created_at=new_track['created_at'],
                    last_checked_at=new_track['last_checked_at']
                ),
                parse_mode=PARSE_MODE,
                reply_markup=InlineKeyboardMarkup(
                    get_track_keyboard(new_track["id"])
                )
            )
            return ConversationHandler.END


@catch_error(PRICE_HISTORY_ERROR)
@load_data_for_register_user
async def check_track_history(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Получает последнии записи в истории товара."""
    query = update.callback_query
    await query.answer()
    track_id = query.data.split('_')[-1]
    async with aiohttp.ClientSession() as session:
        async with session.get(
            GET_TRACKS_PRICE_HISTORY.format(
                track_id=track_id
            ),
            headers=get_headers(context)
        ) as response:
            writes = await response.json()
            navigate_buttons = [
                [
                    InlineKeyboardButton(
                        'Вернуться к списку товаров ⬅️',
                        callback_data=f'{SHOW_ALL_TRACK}'
                    )
                ]
            ]
            if not writes:
                await query.message.reply_text(
                    'История товара пуста(',
                    reply_markup=InlineKeyboardMarkup(navigate_buttons)
                )
                return
            await query.message.reply_text(
                f'История товара {track_id}'
            )
            for write in writes:
                date, time = write['created_at'].split('T')
                await query.message.reply_text(
                    text=PRICE_HISTORY_CARD.format(
                        price=write['price'],
                        date=date,
                        time=time
                    ),
                    parse_mode=PARSE_MODE
                )
            await query.message.reply_text(
                'Навигация 📋',
                reply_markup=InlineKeyboardMarkup(navigate_buttons)
            )


async def confirm_track_delete(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    track_id = query.data.split('_')[-1]
    context.user_data['deleted_track'] = dict()
    context.user_data['deleted_track']['id'] = track_id
    buttons = [
        [
            InlineKeyboardButton(
                'Подтвердить 🖱️',
                callback_data=CONFIRM_DELETE
            ),
            InlineKeyboardButton(
                'Назад ⬅️',
                callback_data=CANCEL_DELETE
            )
        ]
    ]
    await query.message.reply_text(
        f'Вы точно хотите удалить товар с id = {track_id}',
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return FINISH_DELETE_TRACK

@catch_error(DELETE_TRACK_ERROR, conv=True)
@load_data_for_register_user
async def finish_delete_track(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    buttons = [
        [
            InlineKeyboardButton(
                'К списку товаров ⬅️',
                callback_data=SHOW_ALL_TRACK
            )
        ]
    ]
    if query.data == CANCEL_DELETE:
        await query.message.reply_text(
            f'Удаление товара с id = '
            f'{context.user_data["deleted_track"]["id"]} отменено!',
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return ConversationHandler.END
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            DELETE_TRACK_BY_ID.format(
                id=context.user_data['deleted_track']['id']
            )
        ):
            await query.message.reply_text(
                f'Товар с id = {context.user_data["deleted_track"]["id"]} '
                f'успешно удален! ✅',
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    return ConversationHandler.END


def handlers_installer(
    application: ApplicationBuilder
) -> None:
    application.add_handler(
        CallbackQueryHandler(
            show_all, pattern=f'^{SHOW_ALL_TRACK}$'
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            check_track_history, pattern=f'^{CHECK_HISTORY}_'
        )
    )
    refresh_target_price_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                get_new_target_price, pattern='^track_refresh_target_price_'
            )
        ],
        states={
            'save_new_target_price': [
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
                select_marketplace, pattern=f'^{ADD_TRACK}$'
            )
        ],
        states={
            ADD_TRACK_ADD_ARTICLE: [
                CallbackQueryHandler(
                    add_article, pattern=f'^track_({WILDBERRIES}|{OZON})$'
                )
            ],
            ADD_TRACK_ADD_TARGET_PRICE: [
                MessageHandler(
                    MESSAGE_HANDLERS, add_target_price
                )
            ],
            ADD_TRACK_CREATE_NEW_TRACK: [
                MessageHandler(MESSAGE_HANDLERS, create_new_track)
            ]
        },
        fallbacks=[
            MessageHandler(MESSAGE_HANDLERS, create_new_track)
        ]
    )
    delete_track_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                confirm_track_delete, pattern='^track_delete_'
            )
        ],
        states={
            FINISH_DELETE_TRACK: [
                CallbackQueryHandler(
                    finish_delete_track,
                    pattern=f'^({CONFIRM_DELETE}|{CANCEL_DELETE})$'
                )
            ]
        },
        fallbacks=[
            CallbackQueryHandler(
                finish_delete_track,
                pattern=f'^({CONFIRM_DELETE}|{CANCEL_DELETE})$'
            )
        ]
    )
    application.add_handler(
        refresh_target_price_conversation_handler
    )
    application.add_handler(
        add_track_conversation_handler
    )
    application.add_handler(
        delete_track_conversation_handler
    )
