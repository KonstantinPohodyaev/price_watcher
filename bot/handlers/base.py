from http import HTTPStatus

import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from bot.endpoints import (GET_JWT_TOKEN, GET_USER_BY_TELEGRAM_ID,
                           REGISTER_USER, USERS_ENDPOINT)
from bot.handlers.pre_process import load_data_for_register_user
from bot.handlers.utils import check_password
from bot.handlers.validators import (
    validate_full_name, validate_email, validate_password
)

MESSAGE_HANDLERS = filters.TEXT & ~filters.COMMAND

INFO = """
Проект Price Watcher
_______________
здесь вы можете отслеживать цены по интересующим вас товарам
на популярных маркетплейсах и получать уведомления,
если цена упала до желаемой!
/start - запуск бота
/info - информация о боте
/account_info - настройки аккаунта
"""


@load_data_for_register_user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if context.user_data.get('account'):
            await update.message.reply_text(
                text=(
                    f'Привет, {context.user_data["account"]["name"]}\\! '
                    f'Чем я тебе могу помочь\\? 👋\n'
                    f'/info \\- информация о боте\n'
                    f'/auth \\- пройти авторизацию\n'
                ),
                parse_mode='MarkdownV2'
            )
        else:
            button = InlineKeyboardButton(
                'Начать регистрацию',
                callback_data='start_registration'
            )
            keyboard = InlineKeyboardMarkup([[button]])
            await update.message.reply_text(
                'Вы не зарегестрированы!',
                reply_markup=keyboard
            )
    except Exception as error:
        await update.message.reply_text(
            'К сожалению возникла ошибка при аутентификации! ❌'
        )
        print(str(error))

async def info(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        INFO
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
