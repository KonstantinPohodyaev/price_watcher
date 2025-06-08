from http import HTTPStatus

import aiohttp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from bot.endpoints import (GET_JWT_TOKEN, REGISTER_USER, USERS_ENDPOINT,
                           USERS_GET_ME, USERS_ME_REFRESH)
from bot.handlers.constants import MESSAGE_HANDLERS
from bot.handlers.pre_process import load_data_for_register_user
from bot.handlers.utils import (check_authorization, check_password,
                                get_headers, get_interaction)
from bot.handlers.validators import (validate_email, validate_full_name,
                                     validate_password)

# Состояния для ConversationHandler

REGISTRATION_FULL_NAME = 'full_name'
REGISTRATION_EMAIL = 'email'
REGISTRATION_PASSWORD = 'password'

AUTH_AUTHORIZATION = 'auth'
AUTH_GET_PASSWORD = 'get_password'

DELETE_START_DELETE = 'start_delete'

EDIT_CHOOSE_EDIT_FIELD = 'choose_edit_field'
EDIT_START_EDIT_FIELD = 'start_edit_field'
EDIT_SAVE_EDIT_FULL_NAME = 'save_edit_full_name'
EDIT_FINISH_EDIT = 'finish_edit'

# Сообщения для reply_text

ACCOUNT_INFO = """
Настройки аккаунта
__________________
/edit_account - редактировать аккаунт
/delete_account - удалить аккаунт
/account_data - посмотреть данные аккаунта
"""


async def account_info(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    interaction = await get_interaction(update)
    buttons = [
        [
            InlineKeyboardButton(
                'Меню', callback_data='base_menu'
            )
        ]
    ]
    await interaction.message.reply_text(
        ACCOUNT_INFO,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@load_data_for_register_user
async def check_account_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    # buttons = 
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
    return REGISTRATION_FULL_NAME


async def select_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_name = update.message.text
    if not await validate_full_name(update, context, full_name):
        return 'full_name'
    name, surname = full_name.split()
    context.user_data['account']['name'] = name
    context.user_data['account']['surname'] = surname
    await update.message.reply_text(
        'Укажите Вашу почту: '
    )
    return REGISTRATION_EMAIL


async def select_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entered_email = update.message.text
    if not await validate_email(update, context, entered_email):
        return 'email'
    context.user_data['account']['email'] = update.message.text
    await update.message.reply_text(
        'Придумайте пароль: '
    )
    return REGISTRATION_PASSWORD


async def select_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entered_password = update.message.text
    if not await validate_password(update, context, entered_password):
        return 'password'
    context.user_data['account']['password'] = entered_password
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
    return AUTH_AUTHORIZATION


@load_data_for_register_user
async def authorization(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    entered_password = update.message.text
    try:
        async with aiohttp.ClientSession() as session:
            if not await check_password(
                update,
                context,
                entered_password,
                context.user_data['account']['hashed_password']
            ):
                return 'authorization'
            request_body = dict(
                grant_type='password',
                username=context.user_data['account']['email'],
                password=entered_password,
                scope=''
            )
            async with session.post(
                GET_JWT_TOKEN, data=request_body
            ) as response:
                data = await response.json()
                context.user_data['account']['jwt_token'] = data['access_token']
            async with session.patch(
                USERS_ME_REFRESH,
                headers=get_headers(context),
                json=dict(
                    jwt_token=dict(
                        access_token=context.user_data['account']['jwt_token']
                    )
                )
            ) as response:
                if response.status == 200:
                    buttons = [
                        [
                            InlineKeyboardButton(
                                'Меню', callback_data='base_menu'
                            )
                        ]
                    ]
                    await update.message.reply_text(
                        'Авторизация выполнена ✅',
                        reply_markup=InlineKeyboardMarkup(buttons)
                    )
                    return ConversationHandler.END
                await update.message.reply_text(
                        'Ошибка при сохранении новго токена в БД 🚫'
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
    return DELETE_START_DELETE


@load_data_for_register_user
async def delete_account(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    entered_password = update.message.text
    try:
        async with aiohttp.ClientSession() as session:
            if not await check_password(
                update, context,
                entered_password,
                context.user_data['account']['hashed_password']
            ):
                return 'delete_account'
            if not await check_authorization(update, context):
                return ConversationHandler.END
            async with session.delete(
                USERS_ENDPOINT + f'/{context.user_data["account"]["id"]}',
                headers=dict(
                    Authorization=(
                        f'Bearer {context.user_data["account"]["jwt_token"]}'
                    )
                )
            ):
                context.user_data.pop('account')
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


EDIT_FULL_NAME_CALLBACK = 'edit_full_name'
EDIT_EMAIL_CALLBACK = 'edit_email'
EDIT_PASSWORD = 'edit_password'



async def get_password_for_edit_account(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['edit_account'] = dict()
    await update.message.reply_text(
        'Введите пароль от вашего аккаунта:'
    )
    return 'choose_edit_field'


@load_data_for_register_user
async def choose_edit_field(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    entered_password = update.message.text
    try:
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            config = query
        else:
            config = update
        if not await check_password(
            config,
            context,
            entered_password,
            context.user_data['account']['hashed_password']
        ):
            return 'choose_edit_field'
        if not await check_authorization(config, context):
            return ConversationHandler.END
        buttons = [
            [
                InlineKeyboardButton(
                    'Полное имя', callback_data=EDIT_FULL_NAME_CALLBACK
                ),
                InlineKeyboardButton(
                    'Почта', callback_data=EDIT_EMAIL_CALLBACK
                ),
                InlineKeyboardButton(
                    'Пароль', callback_data=EDIT_PASSWORD
                )
            ],
            [
                InlineKeyboardButton(
                    'Применить ✅', callback_data='finish_edit'
                )
            ]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            'Выберите поле для редактирования ⏳',
            reply_markup=keyboard
        )
        return EDIT_START_EDIT_FIELD
    except Exception as error:
        await update.message.reply_text(
            'Ошибка при выборе поля редактирования! 🚫'
        )
        print(str(error))
        return ConversationHandler.END


async def start_edit_field(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    try:
        query = update.callback_query
        await query.answer()
        field = query.data
        if field == EDIT_FULL_NAME_CALLBACK:
            await query.message.reply_text(
                'Введите ваши фамилию и имя:'
            )
            return 'save_edit_full_name'
        elif field == EDIT_EMAIL_CALLBACK:
            await query.message.reply_text(
                'Введите обновленную почту:'
            )
            return 'save_edit_email'
        elif field == EDIT_PASSWORD:
            await query.message.reply_text(
                'Введите новый пароль:'
            )
            return 'save_edit_email'
    except Exception as error:
        await update.message.reply_text(
            'Ошибка при редактировании! 🚫'
        )
        print(str(error))
        return ConversationHandler.END


async def save_edit_full_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    try:
        full_name = update.message.text
        if not await validate_full_name(update, context, full_name):
            return ConversationHandler.END
        name, surname = full_name.split()
        context.user_data['edit_account']['name'] = name
        context.user_data['edit_account']['surname'] = surname
        await update.message.reply_text(
            'Новое имя и фамилия сохранены!\n'
        )
        buttons = [
            [
                InlineKeyboardButton(
                    'Полное имя', callback_data=EDIT_FULL_NAME_CALLBACK
                ),
                InlineKeyboardButton(
                    'Почта', callback_data=EDIT_EMAIL_CALLBACK
                ),
                InlineKeyboardButton(
                    'Пароль', callback_data=EDIT_PASSWORD
                )
            ],
            [
                InlineKeyboardButton(
                    'Применить ✅', callback_data='finish_edit'
                )
            ]
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            'Выберите поле для редактирования ⏳',
            reply_markup=keyboard
        )
        return EDIT_START_EDIT_FIELD
        
    except Exception as error:
        await update.message.reply_text(
            'Ошибка при сохранении новых данных о имени и фамилии в БД 🚫'
        )
        print(str(error))
        return ConversationHandler.END


async def finish_edit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    try:
        async with aiohttp.ClientSession() as session:
            print(context.user_data['edit_account'])
            async with session.patch(
                USERS_ME_REFRESH,
                headers=dict(
                    Authorization=(
                        f'Bearer {context.user_data["account"]["jwt_token"]}'
                    )
                ),
                json=context.user_data['edit_account']
            ) as response:
                new_user_data = await response.json()
                buttons=[
                    [
                        InlineKeyboardButton(
                            'Назад', callback_data='account_info'
                        )
                    ]
                ]
                await query.message.reply_text(
                    f'Данные обновлены ✅\n'
                    f'```python{new_user_data}```',
                    reply_markup=InlineKeyboardMarkup(
                        buttons
                    )
                )
                return ConversationHandler.END
    except Exception as error:
        await query.message.reply_text(
            'Ошибка при сохранении изменений аккаунта 🚫'
        )
        print(str(error))
        return ConversationHandler.END


def handlers_installer(
    application: ApplicationBuilder
) -> None:
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex('^Ваш аккаунт 📱$'),
            account_info
        )
    )
    application.add_handler(
        CommandHandler('account_info', account_info)
    )
    application.add_handler(
        CallbackQueryHandler(account_info, pattern='^account_info$')
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
            REGISTRATION_FULL_NAME: [
                MessageHandler(MESSAGE_HANDLERS, select_name)
            ],
            REGISTRATION_EMAIL: [
                MessageHandler(MESSAGE_HANDLERS, select_email)
            ],
            REGISTRATION_PASSWORD: [
                MessageHandler(MESSAGE_HANDLERS, select_password)
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
            MessageHandler(
                filters.TEXT & filters.Regex('^Авторизация 🔐$'),
                get_password_for_authorization
            )
        ],
        states={
            AUTH_AUTHORIZATION: [
                MessageHandler(MESSAGE_HANDLERS, authorization)
            ],
            AUTH_GET_PASSWORD: [
                MessageHandler(MESSAGE_HANDLERS, get_password_for_authorization)
            ]
        },
        fallbacks=[
            MessageHandler(MESSAGE_HANDLERS, authorization)
        ]
    )
    delete_account_conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                'delete_account', get_password_for_delete_account
            )
        ],
        states={
            DELETE_START_DELETE: [
                MessageHandler(MESSAGE_HANDLERS, delete_account)
            ]
        },
        fallbacks=[
            MessageHandler(MESSAGE_HANDLERS, delete_account)
        ]
    )
    edit_account_conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('edit_account', get_password_for_edit_account)
        ],
        states={
            EDIT_CHOOSE_EDIT_FIELD: [
                MessageHandler(MESSAGE_HANDLERS, choose_edit_field)
            ],
            EDIT_START_EDIT_FIELD: [
                CallbackQueryHandler(start_edit_field, pattern='^edit_')
            ],
            EDIT_SAVE_EDIT_FULL_NAME: [
                MessageHandler(MESSAGE_HANDLERS, save_edit_full_name)
            ],
            EDIT_FINISH_EDIT: [
                CallbackQueryHandler(finish_edit, pattern='^finish_edit$')
            ]
        },
        fallbacks=[
            CallbackQueryHandler(finish_edit, pattern='^finish_edit$')
        ]
    )
    application.add_handler(
        registration_conversation_handler
    )
    application.add_handler(
        authorization_conversation_handler
    )
    application.add_handler(
        delete_account_conversation_handler
    )
    application.add_handler(
        edit_account_conversation_handler
    )
