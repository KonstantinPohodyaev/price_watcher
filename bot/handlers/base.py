from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          filters)

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
/info - информация о боте
/account_info - настройки аккаунта
"""

START_MESSAGE = (
    '<b>Привет</b>, <code>{name}</code>! '
    'Чем я тебе могу помочь? 👋\n'
    '/info - информация о боте\n'
    '/auth - пройти авторизацию\n'
)


@load_data_for_register_user
@catch_error(START_ERROR)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('account'):
        keyboard = None
        if context.user_data['account'].get('jwt_token'):
            buttons = [
                [
                    InlineKeyboardButton(
                        'Мои товары 📦', callback_data='track_show_all'
                    )
                ]
            ]
            keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            text=START_MESSAGE.format(
                name=update.message.from_user.username
            ),
            parse_mode=PARSE_MODE,
            reply_markup=keyboard
        )
    else:
        button = InlineKeyboardButton(
            'Начать регистрацию 🔥',
            callback_data='start_registration'
        )
        keyboard = InlineKeyboardMarkup([[button]])
        await update.message.reply_text(
            'Вы не зарегестрированы! 🚨',
            reply_markup=keyboard
        )


async def info(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        text=INFO,
        parse_mode=PARSE_MODE
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
