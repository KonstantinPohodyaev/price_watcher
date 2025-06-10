from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, Update)
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, filters)

from bot.handlers.callback_data import (ADD_TRACK, MENU, SHOW_ALL_TRACK,
                                        START_REGISTRATION)
from bot.handlers.constants import PARSE_MODE
from bot.handlers.pre_process import load_data_for_register_user
from bot.handlers.utils import catch_error

MESSAGE_HANDLERS = filters.TEXT & ~filters.COMMAND

START_ERROR = 'К сожалению возникла ошибка при запуске бота! ❌'

INFO = """
<u>Проект Price Watcher</u>
_____________________________
здесь вы можете отслеживать цены по интересующим вас товарам
на популярных маркетплейсах и получать уведомления,
если цена упала до желаемой!
/start - запуск бота
/auth - пройти авторизацию
/account_info - настройки аккаунта
"""

START_MESSAGE = """
<b>Привет</b>, <code>{name}</code>!
Чем я тебе могу помочь? 👋
/info - информация о боте
"""

MAIN_REPLY_BUTTONS = ['Старт 🔥', 'Авторизация 🔐', 'Ваш аккаунт 📱']


@load_data_for_register_user
@catch_error(START_ERROR)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    main_keyboard = ReplyKeyboardMarkup(
        [MAIN_REPLY_BUTTONS],
        resize_keyboard=True
    )
    if context.user_data.get('account'):
        if context.user_data['account'].get('jwt_token'):
            buttons = [
                [
                    InlineKeyboardButton(
                        'Меню 📦', callback_data=MENU
                    )
                ]
            ]
        await update.message.reply_text(
            'Загрузка интерфейса...',
            reply_markup=main_keyboard
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
    await update.message.reply_text(
        text=INFO,
        parse_mode=PARSE_MODE
    )


async def menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    buttons = [
        [
            InlineKeyboardButton(
                'Мои товары 📦',
                callback_data=SHOW_ALL_TRACK
            )
        ],
        [
            InlineKeyboardButton(
                'Добавить новый товар 📦',
                callback_data=ADD_TRACK
            )
        ],
        
    ]
    await query.message.reply_text(
        'Выберите интересующий вас пункт',
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
        CallbackQueryHandler(menu, pattern=f'^{MENU}$')
    )
