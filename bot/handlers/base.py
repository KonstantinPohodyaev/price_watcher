from http import HTTPStatus

import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from bot.endpoints import (GET_JWT_TOKEN, GET_USER_BY_TELEGRAM_ID,
                           REGISTER_USER, USERS_ENDPOINT)
from bot.handlers.pre_process import load_data_for_register_user
from bot.handlers.utils import check_password, load_user_data
from bot.handlers.validators import validate_full_name

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

ACCOUNT_INFO = """
Настройки аккаунта
__________________
/delete_account - удалить аккаунт
/account_data - посмотреть данные аккаунта
"""


@load_data_for_register_user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if context.user_data['account']:
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


async def account_info(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        ACCOUNT_INFO
    )


async def check_account_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        text=f'```{context.user_data["account"]}```',
        parse_mode='MarkdownV2'
    )


async def start_registration(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик начала регистрации пользователя."""
    query = update.callback_query
    await query.answer()
    context.user_data['account'] = dict()
    await query.message.reply_text(
        'Укажите Ваше имя и фамилию через пробел: '
    )
    return 'name_and_surname'


async def select_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not validate_full_name(update.message.text):
        await update.message.reply_text(
            'Неверный формат ввода имени и фамилии 🚫\n'
            'Попробуйте еще раз:'
        )
        return 'name_and_surname'
    name, surname = update.message.text.split()
    context.user_data['account']['name'] = name
    context.user_data['account']['surname'] = surname
    await update.message.reply_text(
        'Укажите Вашу почту: '
    )
    return 'email'


async def select_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['account']['email'] = update.message.text
    await update.message.reply_text(
        'Придумайте пароль: '
    )
    return 'password'


async def select_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['account']['password'] = update.message.text
    context.user_data['account']['telegram_id'] = update.message.from_user.id
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                REGISTER_USER, json=context.user_data['account']
            ) as response:
                if response.status == HTTPStatus.CREATED:
                    user = await response.json()
                    await update.message.reply_text(
                        'Регистрация закончена!'
                    )
                    buttons = [
                        [
                            InlineKeyboardButton(
                                'Авторизация', callback_data='authorization'
                            )
                        ]
                    ]
                    await update.message.reply_text(
                        text=(
                            f'Привет, {user["name"]}! '
                            f'Вот твой id: {user["id"]}'
                        ),
                        reply_markup=InlineKeyboardMarkup(buttons)
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


async def get_password_for_authorization(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        config = query
    else:
        config = update
    await config.message.reply_text(
        'Введите пароль от вашего аккаунта:'
    )
    return 'authorization'


async def authorization(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if not context.user_data.get('account'):
        context.user_data['account'] = dict()
    context.user_data['account']['password'] = update.message.text
    try:
        async with aiohttp.ClientSession() as session:
            await load_user_data(
                session, update, context
            )
            if not check_password(
                context.user_data['account']['password'],
                context.user_data['account']['hashed_password']
            ):
                await update.message.reply_text(
                    'Вы ввели неправильный пароль 🚫\n'
                    'Попробуйте еще раз.'
                )
                return 'authorization'
            if context.user_data['account'].get('jwt_token'):
                print(context.user_data['account'].get('jwt_token'))
                await update.message.reply_text(
                    'Авторизация уже пройдена!'
                )
                return ConversationHandler.END
            else:
                request_body = dict(
                    grant_type='password',
                    username=context.user_data['account']['email'],
                    password=context.user_data['account']['password'],
                    scope=''
                )
                async with session.post(
                    GET_JWT_TOKEN, data=request_body
                ) as response:
                    data = await response.json()
                    context.user_data['account']['jwt_token'] = (
                        data['access_token']
                    )
                    await update.message.reply_text(
                        'Авторизация выполнена ✅'
                    )
                    return ConversationHandler.END
    except Exception as error:
        await update.message.reply_text(
            'Ошибка при получении JWT-токена. Повторите регистрацию.'
        )
        print(str(error))
        return ConversationHandler.END


async def get_password_for_delete_account(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        'Введите пароль от вашего аккаунта:'
    )
    return 'start_delete'


async def delete_account(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if not context.user_data.get('account'):
        context.user_data['account'] = dict()
    context.user_data['account']['password'] = update.message.text
    try:
        async with aiohttp.ClientSession() as session:
            await load_user_data(session, update, context)
            if not check_password(
                context.user_data['account']['password'],
                context.user_data['account']['hashed_password']
            ):
                await update.message.reply_text(
                    'Вы ввели неправильный пароль 🚫\n'
                    'Попробуйте еще раз.'
                )
                return 'delete_account'
            if not context.user_data['account'].get('jwt_token'):
                await update.message.reply_text(
                    'Для удаления аккаунта необходима авторизация'
                )
                return ConversationHandler.END
            async with session.delete(
                USERS_ENDPOINT + f'/{context.user_data["account"]["id"]}',
                headers=dict(
                    Authorization=(
                        f'Bearer {context.user_data["account"]["jwt_token"]}'
                    )
                )
            ):
                await update.message.reply_text(
                    'Ваш акккаунт удален!'
                    'Вы можете зарегестрироваться снова - /start'
                )
                return ConversationHandler.END
    except Exception as error:
        await update.message.reply_text(
            'Ошибка при удалении аккаунта.'
        )
        print(str(error))


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
        CommandHandler('account_info', account_info)
    )
    application.add_handler(
        CommandHandler('account_data', check_account_data)
    )
    registration_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                start_registration, pattern='^start_registration$'
            )
        ],
        states={
            'name_and_surname': [
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
    authorization_conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                get_password_for_authorization, pattern='^authorization$'
            ),
            CommandHandler(
                'auth', get_password_for_authorization
            ),
        ],
        states={
            'authorization': [
                MessageHandler(MESSAGE_HANDLERS, authorization)
            ],
            'get_password': [
                MessageHandler(MESSAGE_HANDLERS, get_password_for_authorization)
            ]
        },
        fallbacks=[
            MessageHandler(MESSAGE_HANDLERS, authorization)
        ]
    )
    delete_acoount_conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                'delete_account', get_password_for_delete_account
            )
        ],
        states={
            'start_delete': [
                MessageHandler(MESSAGE_HANDLERS, delete_account)
            ]
        },
        fallbacks=[
            MessageHandler(MESSAGE_HANDLERS, delete_account)
        ]
    )
    application.add_handler(
        registration_conversation_handler
    )
    application.add_handler(
        authorization_conversation_handler
    )
    application.add_handler(
        delete_acoount_conversation_handler
    )
