from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, Update)
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, MessageHandler,
                          filters)

from bot.handlers.buttons import REPLY_KEYBOARD
from bot.handlers.callback_data import (ADD_TRACK, MENU, SHOW_ALL_TRACK,
                                        START_AUTHORIZATION,
                                        START_NOTIFICATIONS,
                                        START_REGISTRATION, BOT_INFO)
from bot.handlers.constants import PARSE_MODE
from bot.handlers.pre_process import load_data_for_register_user, load_option_features
from bot.handlers.utils import (catch_error, check_authorization,
                                get_interaction, add_message_to_delete_list)
from bot.scheduler import (PERIODIC_CHECK_FIRST, PERIODIC_CHECK_INTERVAL,
                           periodic_check)

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
/account_info — настройки аккаунта
/menu — главное меню
"""

START_MESSAGE = """
<b>👋 Привет, <code>{name}</code>!</b>  
Добро пожаловать в <b>Price Watcher</b>  
━━━━━━━━━━━━━━━━━━━━━━━━━━  
Я помогу тебе следить за ценами и вовремя сообщать,  
когда товар подешевеет 📉  
━━━━━━━━━━━━━━━━━━━━━━━━━━  
ℹ️ /info — информация о боте
"""

@catch_error(START_ERROR)
@load_data_for_register_user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('account'):
        if context.user_data['account'].get('jwt_token'):
            buttons = [
                [
                    InlineKeyboardButton(
                        'Меню 📦', callback_data=MENU
                    )
                ]
            ]
        else:
            buttons = [
                [
                   InlineKeyboardButton(
                        'Авторизация 📦', callback_data=START_AUTHORIZATION
                    )
                ]
            ]
        await update.message.reply_text(
            'Загрузка интерфейса...',
            reply_markup=REPLY_KEYBOARD
        )
        await update.message.reply_text(
            text=START_MESSAGE.format(
                name=update.message.from_user.username
            ),
            parse_mode=PARSE_MODE,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        buttons = [
            [
                InlineKeyboardButton(
                    'Начать регистрацию 🔥',
                    callback_data=START_REGISTRATION
                )
            ]
        ]
        await update.message.reply_text(
            'Вы не зарегестрированы! 🚨',
            reply_markup=InlineKeyboardMarkup(buttons)
        )


async def info(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    interaction = await get_interaction(update)
    await interaction.message.reply_text(
        text=INFO_MESSAGE,
        parse_mode=PARSE_MODE
    )

async def menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    interaction = await get_interaction(update)
    buttons = [
        [
            InlineKeyboardButton(
                text='📦 Мои товары',
                callback_data=SHOW_ALL_TRACK
            )
        ],
        [
            InlineKeyboardButton(
                text='➕ Добавить товар',
                callback_data=ADD_TRACK
            )
        ],
        [
            InlineKeyboardButton(
                text='🔔 Включить оповещения',
                callback_data=START_NOTIFICATIONS
            )
        ],
        [
            InlineKeyboardButton(
                text='ℹ️ О боте',
                callback_data=BOT_INFO
            )
        ],
    ]
    message = await interaction.message.reply_text(
        'Выберите интересующий вас пункт',
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    add_message_to_delete_list(message, context)

@catch_error(START_NOTIFICARIONS_ERROR)
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
    buttons = [
        [
            InlineKeyboardButton(
                'Перейти в меню 📋',
                callback_data=MENU
            )
        ]
    ]
    await query.message.reply_text(
        '✅ Уведомления о снижении цены включены.',
        reply_markup=InlineKeyboardMarkup(buttons)
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
        MessageHandler(
            filters.TEXT & filters.Regex('^Меню 🔥$'), menu
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            start_notifications, pattern=f'^{START_NOTIFICATIONS}$'
        )
    )
