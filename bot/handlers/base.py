from http import HTTPStatus

import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ApplicationBuilder, CallbackQueryHandler,
    CommandHandler, ConversationHandler, MessageHandler, filters
    )

from bot.endpoints import GET_USER_BY_TELEGRAM_ID, REGISTER_USER


MESSAGE_HANDLERS = filters.TEXT & ~filters.COMMAND


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GET_USER_BY_TELEGRAM_ID,
                json=dict(telegram_id=int(update.message.from_user.id))
            ) as response:
                current_user = await response.json()
                if current_user:
                    await update.message.reply_text(
                        f'Привет, {current_user["name"]}! '
                        f'Чем я тебе могу помочь? 👋'
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


async def start_registration(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик начала регистрации пользователя."""
    query = update.callback_query
    await query.answer()
    context.user_data['user_data'] = dict()
    await query.message.reply_text(
        'Укажите Ваше имя: '
    )
    return 'name'


async def select_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_data']['name'] = update.message.text
    await update.message.reply_text(
        'Укажите Вашу почту: '
    )
    return 'email'


async def select_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_data']['email'] = update.message.text
    await update.message.reply_text(
        'Придумайте пароль: '
    )
    return 'password'


async def select_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_data']['password'] = update.message.text
    context.user_data['user_data']['telegram_id'] = update.message.from_user.id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                REGISTER_USER, json=context.user_data['user_data']
            ) as response:
                if response.status == HTTPStatus.CREATED:
                    user = await response.json()
                    await update.message.reply_text(
                        'Регистрация закончена!'
                    )
                    await update.message.reply_text(
                        f'Привет, {user["name"]}! Вот твой id: {user["id"]}'
                    )
                else:
                    detail = await response.json()
                    await update.message.reply_text(detail)
    except Exception as error:
        await update.message.reply_text(
            'Возникла ошибка при регистрации пользователя('
        )
        print(str(error))
    return ConversationHandler.END


def handlers_installer(
    application: ApplicationBuilder
) -> None:
    application.add_handler(
        CommandHandler('start', start)
    )
    registration_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                start_registration, pattern='start_registration'
            )
        ],
        states={
            'name': [
                MessageHandler(MESSAGE_HANDLERS, select_name)
            ],
            'email': [
                MessageHandler(MESSAGE_HANDLERS, select_email)
            ]
        },
        fallbacks=[
            MessageHandler(MESSAGE_HANDLERS, select_password)
        ]
    )
    application.add_handler(
        registration_conversation_handler
    )
