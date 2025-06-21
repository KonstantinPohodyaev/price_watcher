from decimal import Decimal
from http import HTTPStatus

import aiohttp
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          ContextTypes, ConversationHandler, MessageHandler)

from bot.endpoints import (CREATE_NEW_TRACK, DELETE_TRACK_BY_ID,
                           GET_TRACKS_PRICE_HISTORY, USERS_TRACKS,
                           USERS_TRACKS_BY_ID)
from bot.handlers.buttons import (CHECK_HISTORY_BUTTONS,
                                  CONFIRM_TRACK_DELETE_BUTTONS,
                                  FINISH_DELETE_TRACK_BUTTONS,
                                  GO_BACK_NEW_TARGET_PRICE_BUTTONS,
                                  SELECT_MARKETPLACE_BUTTONS, SHOW_ALL_BUTTONS,
                                  get_create_track_buttons, get_track_keyboard)
from bot.handlers.callback_data import (ADD_TRACK, CANCEL_DELETE,
                                        CHECK_HISTORY, CONFIRM_DELETE,
                                        DELETE_TRACK, OZON,
                                        SHOW_ALL_TRACK, WILDBERRIES)
from bot.handlers.constants import MESSAGE_HANDLERS, PARSE_MODE
from bot.handlers.pre_process import (clear_messages,
                                      load_data_for_register_user)
from bot.handlers.utils import (catch_error, check_authorization, get_headers,
                                get_interaction, send_tracked_message)
from bot.handlers.validators import validate_price

# Состояния для ConversationHandler
SAVE_NEW_TARGET_PRICE = 'save_new_target_price'

ADD_TRACK_ADD_ARTICLE = 'add_article'
ADD_TRACK_ADD_TARGET_PRICE = 'add_target_price'
ADD_TRACK_CREATE_NEW_TRACK = 'create_new_track'

FINISH_DELETE_TRACK = 'delete_track'

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
<b>🛒 {title}</b>  <code>{article}</code>
_____________________________________
💸 <b>Текущая цена:</b> <code>{current_price}₽</code>
🎯 <b>Желаемая цена:</b> <code>{target_price}₽</code>
🏷️ <b>Статус:</b> {status}
_____________________________________
<b>ID:</b> <code>{id}</code>
"""
PRICE_HISTORY_CARD = """
<b>💰 Цена:</b> {price}₽
<b>📅 Дата:</b> {date} {time}
"""
TRACKS_RESULT_MESSAGE = """
<b>📊 Итого:</b>
_____________________________________
<b>📦 Всего отслеживаемых товаров:</b> <code>{track_count}</code>
<b>📉 Цена ниже желаемой:</b> <code>{true_track_count}</code>
<b>📈 Цена выше желаемой:</b> <code>{false_track_count}</code>
"""


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

NEW_TARGET_PRICE_MESSAGE = """
{track_card}
_________________________
Укажите новую желаемую цену 🏷️
"""
SUCCESS_SAVE_NEW_TARGET_PRICE_MESSAGE = (
    'Цена успешно обновлена на {new_target_price}! ✅'
)
EMPTY_TRACK_HISTORY_MESSAGE = 'История товара пуста('
TRACK_HISTORY_MESSAGE = """
📊 История товара {track_id}
_________________________
{track_card}
"""
TRACK_HISTORY_NAVIGATION = 'Навигация 📋'
CONFIRM_DELETE_MESSAGE = """
{track_card}
_________________________
Вы точно хотите удалить товар с id = {track_id}
"""
CANCEL_DELETE_MESSAGE = 'Удаление товара с id = {track_id} отменено!'
SUCCESS_DELETE_MESSAGE = 'Товар с id = {track_id} успешно удален! ✅'


@catch_error(SHOW_ALL_ERROR)
@clear_messages
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
                await send_tracked_message(
                    query,
                    context,
                    text=OUTDATED_AUTHORIZATION_ERROR
                )
                return
            tracks = await response.json()
            if not tracks:
                await send_tracked_message(
                    query,
                    context,
                    text=EMPTY_TRACKS
                )
            true_track_count = false_track_count = 0
            for track in tracks:
                if Decimal(track['target_price']) >= Decimal(track['current_price']):
                    true_track_count += 1
                else:
                    false_track_count += 1
                track_card = SHORT_TRACK_CARD.format(
                    title=track.get('title'),
                    id=track.get('id'),
                    article=track.get('article'),
                    current_price=track.get('current_price'),
                    target_price=track.get('target_price'),
                    status='✅' if track['notified'] else '❌'
                )
                await send_tracked_message(
                    query,
                    context,
                    text=track_card,
                    reply_markup=InlineKeyboardMarkup(
                        get_track_keyboard(track["id"])
                    )
                )
            await send_tracked_message(
                query,
                context,
                text=TRACKS_RESULT_MESSAGE.format(
                    track_count=len(tracks),
                    true_track_count=true_track_count,
                    false_track_count=false_track_count
                ),
                reply_markup=InlineKeyboardMarkup(SHOW_ALL_BUTTONS)
            )


async def get_new_target_price(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    context.user_data['track_id'] = query.data.split('_')[-1]
    if not await check_authorization(query, context):
        return ConversationHandler.END
    await query.message.edit_text(
        text=NEW_TARGET_PRICE_MESSAGE.format(
            track_card=query.message.text
        ),
        parse_mode=PARSE_MODE
    )
    return SAVE_NEW_TARGET_PRICE


@catch_error(TRACK_REFRESH_ERROR, conv=True)
@clear_messages
@load_data_for_register_user
async def target_price_refresh(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    new_target_price = update.message.text
    await update.message.delete()
    validated_price = await validate_price(
        update, context, new_target_price
    )
    if not validated_price:
        return SAVE_NEW_TARGET_PRICE
    async with aiohttp.ClientSession() as session:
        refresh_data = dict(
            target_price=validated_price
        )
        async with session.patch(
            USERS_TRACKS_BY_ID.format(id=context.user_data['track_id']),
            headers=get_headers(context),
            json=refresh_data
        ):
            await send_tracked_message(
                update,
                context,
                text=SUCCESS_SAVE_NEW_TARGET_PRICE_MESSAGE.format(
                    new_target_price=new_target_price
                ),
                reply_markup=InlineKeyboardMarkup(
                    GO_BACK_NEW_TARGET_PRICE_BUTTONS
                )
            )
            return ConversationHandler.END


@clear_messages
async def select_marketplace(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['new_track'] = dict()
    interaction = await get_interaction(update)
    await send_tracked_message(
        interaction,
        context,
        text=SELECT_MARKETPLACE_MESSAGE,
        reply_markup=InlineKeyboardMarkup(SELECT_MARKETPLACE_BUTTONS)
    )
    return ADD_TRACK_ADD_ARTICLE


@clear_messages
async def add_article(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    context.user_data['new_track']['marketplace'] = query.data.split('_')[-1]
    await send_tracked_message(
        query,
        context,
        text=SELECT_ARTICLE_MESSAGE
    )
    return ADD_TRACK_ADD_TARGET_PRICE


@clear_messages
async def add_target_price(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['new_track']['article'] = update.message.text
    await update.message.delete()
    await send_tracked_message(
        update,
        context,
        text=SELECT_TARGET_PRICE_MESSAGE
    )
    return ADD_TRACK_CREATE_NEW_TRACK


@catch_error(CREATE_NEW_TRACK_ERROR, conv=True)
@clear_messages
@load_data_for_register_user
async def create_new_track(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    target_price = await validate_price(
        update,
        context,
        update.message.text
    )
    if not target_price:
        return ADD_TRACK_CREATE_NEW_TRACK
    context.user_data['new_track']['target_price'] = target_price
    await update.message.delete()
    context.user_data['track_list'] = dict()
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
            await send_tracked_message(
                update,
                context,
                text=SUCCESS_CREATE_TRACK_MESSAGE
            )
            track_card = TRACK_CARD.format(
                title=new_track['title'],
                article=new_track['article'],
                current_price=new_track['current_price'],
                target_price=new_track['target_price'],
                created_at=new_track['created_at'],
                last_checked_at=new_track['last_checked_at']
            )
            context.user_data['track_list'][f'{new_track["id"]}'] = track_card
            await send_tracked_message(
                update,
                context,
                text=track_card,
                reply_markup=InlineKeyboardMarkup(
                    get_create_track_buttons(new_track['id'])
                )
            )
            return ConversationHandler.END


@catch_error(PRICE_HISTORY_ERROR)
@clear_messages
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
            if not writes:
                await query.message.reply_text(
                    EMPTY_TRACK_HISTORY_MESSAGE,
                    reply_markup=InlineKeyboardMarkup(CHECK_HISTORY_BUTTONS)
                )
                return
            await send_tracked_message(
                query,
                context,
                text=TRACK_HISTORY_MESSAGE.format(
                    track_id=track_id,
                    track_card=query.message.text
                )
            )
            for write in writes:
                date, time = write['created_at'].split('T')
                await send_tracked_message(
                    query,
                    context,
                    text=PRICE_HISTORY_CARD.format(
                        price=write['price'],
                        date=date,
                        time=time
                    )
                )
            await send_tracked_message(
                query,
                context,
                text=TRACK_HISTORY_NAVIGATION,
                reply_markup=InlineKeyboardMarkup(CHECK_HISTORY_BUTTONS)
            )


async def confirm_track_delete(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    track_card = query.message.text
    track_id = query.data.split('_')[-1]
    context.user_data['deleted_track'] = dict()
    context.user_data['deleted_track']['id'] = track_id
    await query.message.edit_text(
        text=CONFIRM_DELETE_MESSAGE.format(
            track_card=track_card,
            track_id=track_id
        ),
        reply_markup=InlineKeyboardMarkup(CONFIRM_TRACK_DELETE_BUTTONS),
        parse_mode=PARSE_MODE
    )
    return FINISH_DELETE_TRACK


@catch_error(DELETE_TRACK_ERROR, conv=True)
@clear_messages
@load_data_for_register_user
async def finish_delete_track(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    if query.data == CANCEL_DELETE:
        await send_tracked_message(
            query,
            context,
            text=CANCEL_DELETE_MESSAGE.format(
                track_id=context.user_data['deleted_track']['id']
            ),
            reply_markup=InlineKeyboardMarkup(FINISH_DELETE_TRACK_BUTTONS)
        )
        return ConversationHandler.END
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            DELETE_TRACK_BY_ID.format(
                id=context.user_data['deleted_track']['id']
            ),
            headers=get_headers(context)
        ):
            await send_tracked_message(
                query,
                context,
                text=SUCCESS_DELETE_MESSAGE.format(
                    track_id=context.user_data['deleted_track']['id']
                ),
                reply_markup=InlineKeyboardMarkup(FINISH_DELETE_TRACK_BUTTONS)
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
            SAVE_NEW_TARGET_PRICE: [
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
                confirm_track_delete, pattern=f'^{DELETE_TRACK}_'
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
