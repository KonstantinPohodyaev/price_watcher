from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      Update)
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, MessageHandler,
                          filters)

from bot.handlers.callback_data import MENU, START_NOTIFICATIONS, BOT_INFO
from bot.handlers.pre_process import load_data_for_register_user, clear_messages
from bot.handlers.utils import (catch_error, check_authorization,
                                get_interaction, add_message_to_delete_list,
                                send_tracked_message)
from bot.scheduler import (PERIODIC_CHECK_FIRST, PERIODIC_CHECK_INTERVAL,
                           periodic_check)
from bot.handlers.buttons import (
    MENU_BUTTONS, REGISTER_USER_BUTTONS, NOT_REGISTER_USER_BUTTONS,
    START_REGISTRATION_BUTTONS
)

MESSAGE_HANDLERS = filters.TEXT & ~filters.COMMAND

START_ERROR = 'К сожалению возникла ошибка при запуске бота! ❌'

START_NOTIFICARIONS_ERROR = 'Ошибка при активации уведомлений! ❌'

INFO_MESSAGE = """
<b>📊 Проект: <u>Price Watcher</u></b>  
━━━━━━━━━━━━━━━━━━━━━━━━━━  
🔍 Следи за ценами на товары с популярных маркетплейсов  
📉 Подключи уведомления и узнаешь, когда цена на товар упадет до желаемой  
🔐 Простая авторизация и управление аккаунтом  
━━━━━━━━━━━━━━━━━━━━━━━━━━  
📌 Команды:  
/start — запустить бота  
/auth — авторизация  
/account_settings — настройки аккаунта
/menu — главное меню
"""

START_DECORATING_MESSAGE = 'Загрузка интерфейса...'
START_MESSAGE = """
<b>👋 Привет, <code>{name}</code>!</b>  
Добро пожаловать в <b>Price Watcher</b>  
━━━━━━━━━━━━━━━━━━━━━━━━━━  
Я помогу тебе следить за ценами и вовремя сообщать,  
когда товар подешевеет 📉  
━━━━━━━━━━━━━━━━━━━━━━━━━━  
ℹ️ /info — информация о боте
"""
UNREGISTERED_MESSAGE = 'Вы не зарегестрированы! 🚨'
NOTIFICATION_ON_MESSAGE = '✅ Уведомления о снижении цены включены.'
MENU_MESSAGE = 'Выберите интересующий вас пункт'

START_NOTIFICATIONS_BUTTONS = [
    [
        InlineKeyboardButton(
            'Перейти в меню 📋',
            callback_data=MENU
        )
    ]
]

@catch_error(START_ERROR)
@clear_messages
@load_data_for_register_user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('account'):
        if context.user_data['account'].get('jwt_token'):
            buttons = REGISTER_USER_BUTTONS
        else:
            buttons = NOT_REGISTER_USER_BUTTONS
        await send_tracked_message(
            update,
            context,
            text=START_DECORATING_MESSAGE
        )
        await send_tracked_message(
            update,
            context,
            text=START_MESSAGE.format(
                name=update.message.from_user.username
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        buttons = START_REGISTRATION_BUTTONS
        await send_tracked_message(
            update,
            context,
            text=UNREGISTERED_MESSAGE,
            reply_markup=InlineKeyboardMarkup(buttons)
        )


@clear_messages
async def info(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await send_tracked_message(
        await get_interaction(update),
        context,
        text=INFO_MESSAGE
    )


@clear_messages
async def menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await send_tracked_message(
        await get_interaction(update),
        context,
        text=MENU_MESSAGE,
        reply_markup=InlineKeyboardMarkup(MENU_BUTTONS)
    )


@catch_error(START_NOTIFICARIONS_ERROR)
@clear_messages
@load_data_for_register_user
async def start_notifications(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    if not await check_authorization(query, context):
        return
    context.job_queue.run_repeating(
        periodic_check,
        interval=PERIODIC_CHECK_INTERVAL,
        first=PERIODIC_CHECK_FIRST,
        name=f'price_check_{query.message.chat.id}',
        data=dict(
            jwt_token=context.user_data['account']['jwt_token'],
            chat_id=query.from_user.id
        )
    )
    await send_tracked_message(
        query,
        context,
        text=NOTIFICATION_ON_MESSAGE,
        reply_markup=InlineKeyboardMarkup(START_NOTIFICATIONS_BUTTONS)
    )


def handlers_installer(
    application: ApplicationBuilder
) -> None:
    application.add_handler(
        CommandHandler('start', start)
    )
    application.add_handler(
        CommandHandler('info', info)
    )
    application.add_handler(
        CallbackQueryHandler(info, pattern=f'^{BOT_INFO}$')
    )
    application.add_handler(
        CallbackQueryHandler(menu, pattern=f'^{MENU}$')
    )
    application.add_handler(
        CommandHandler('menu', menu)
    )
    application.add_handler(
        CallbackQueryHandler(
            start_notifications, pattern=f'^{START_NOTIFICATIONS}$'
        )
    )
