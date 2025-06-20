from http import HTTPStatus

import aiohttp
from telegram import InlineKeyboardMarkup, InputFile, Update
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler)

from bot.endpoints import (ADD_NEW_AVATAR, DELETE_USER_BY_ID, GET_JWT_TOKEN,
                           REGISTER_USER, USERS_REFRESH_ME)
from bot.handlers.buttons import (ACCOUNT_SETTINGS_BUTTONS,
                                  CHECK_ACCOUNT_DATA_BUTTONS, EDIT_BUTTONS,
                                  FINISH_AUTHORIZATION_BUTTONS,
                                  FINISH_EDIT_BUTTONS,
                                  FINISH_REGISTRATION_BUTTONS,
                                  LOAD_ACCOUNT_DATA)
from bot.handlers.callback_data import (ACCOUNT_SETTINGS, EDIT_ADD_AVATAR,
                                        EDIT_EMAIL_CALLBACK,
                                        EDIT_FULL_NAME_CALLBACK, EDIT_PASSWORD)
from bot.handlers.constants import MESSAGE_HANDLERS, PHOTO_HANDLERS
from bot.handlers.pre_process import (clear_messages,
                                      load_data_for_register_user)
from bot.handlers.utils import (catch_error, check_authorization,
                                check_password, get_headers, get_interaction,
                                send_tracked_message, send_tracked_photo)
from bot.handlers.validators import (PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH,
                                     validate_email, validate_empty_photo,
                                     validate_full_name, validate_password)

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
EDIT_SAVE_EDIT_EMAIL = 'save_edit_email'
EDIT_SAVE_EDIT_PASSWORD = 'save_edit_password'
EDIT_SAVE_AVATAR = 'save_avatar'
EDIT_FINISH_EDIT = 'finish_edit'

# Сообщения для reply_text

ACCOUNT_SETTINGS_MESSAGE = """
<b>⚙️ Настройки аккаунта</b>
━━━━━━━━━━━━━━━━━━
🔄 <b>/load_data</b> – обновить данные аккаунта
✏️ <b>/edit_account</b> – редактировать аккаунт
🗑️ <b>/delete_account</b> – удалить аккаунт
👤 <b>/account_data</b> – просмотреть данные аккаунта
"""

ACCOUNT_DATA_MESSAGE = """
<b>👤 Данные аккаунта</b>
━━━━━━━━━━━━━━━━━━
<b>Имя:</b> {name}
<b>Фамилия:</b> {surname}
<b>Почта:</b> {email}
<b>Telegram ID:</b> <code>{telegram_id}</code>
<b>Chat ID:</b> <code>{chat_id}</code>

<b>Активен:</b> {active}
<b>Почта подтверждена:</b> {is_verified}
<b>Суперпользователь:</b> {is_superuser}

<b>JWT-токен:</b>
<code>{jwt_token}</code>
"""

ACCOUNT_DATA_NAVIGATION_MESSAGE = """
📍 <b>Навигация</b>
───────────────
⬅️ Назад | 🏠 Меню
"""

USER_CARD = """
👤 <b>Полное имя:</b> {name} {surname}
📧 <b>Почта:</b> <code>{email}</code>
🆔 <b>Telegram ID:</b> <code>{telegram_id}</code>
🔐 <b>JWT:</b> <code>{jwt_token}</code>
"""

LOAD_ACCOUNT_DATA_MESSAGE = 'Данные аккаунта успешно обновлены! ✅'

ASK_FULL_NAME = """
👤 Пожалуйста, введите <b>ваше имя и фамилию</b> через пробел:
Пример: <code>Иван Иванов</code>
"""

ASK_EMAIL = """
📧 Введите <b>вашу электронную почту</b>:
Пример: <code>example@mail.ru</code>
"""

ASK_PASSWORD = """
🔒 Придумайте <b>безопасный пароль</b>:
<i>От {min} до {max} символов, состоящий из цифр</i>
"""

REGISTRATION_SUCCESS = """
✅ <b>Регистрация завершена!</b>
Давайте авторизуемся, чтобы начать пользоваться ботом 👇
"""

REGISTRATION_GREETING_TEMPLATE = """
👋 Добро пожаловать, <b>{name}</b>!
🆔 Ваш уникальный ID: <code>{user_id}</code>
Для продолжения нажмите кнопку ниже ⬇️
"""

ENTER_PASSWORD_MESSAGE = 'Введите пароль от вашего аккаунта:'

NO_ACCOUNT_LOADED = """
⚠️ Не удалось найти данные аккаунта.

Попробуйте обновить командой: <code>/load_data</code>
"""

# Для авторизации
ASK_PASSWORD_AUTH = """
🔑 Введите <b>ваш пароль</b> для авторизации:
"""

INVALID_PASSWORD = """
❌ <b>Неверный пароль</b>. Попробуйте ещё раз:
"""

AUTH_SUCCESS = """
✅ <b>Авторизация прошла успешно!</b>

Выберите действие ниже 👇
"""

# Для удаления аккаунта
ASK_PASSWORD_FOR_DELETE = """
🔐 <b>Введите пароль</b> от вашего аккаунта для подтверждения удаления:
"""

INVALID_PASSWORD_DELETE = """
❌ <b>Неверный пароль</b>. Повторите попытку:
"""

DELETE_SUCCESS = """
🗑️ <b>Ваш аккаунт был успешно удалён!</b>

Вы всегда можете зарегистрироваться снова — /start
"""

# Для редактирования профиля
START_EDIT_PASSWORD_PROMPT = """
🔐 Введите пароль от вашего аккаунта:
"""

CHOOSE_EDIT_FIELD_PROMPT = """
🛠️ Выберите поле для редактирования ⏳
После редактирования нажмите применить!
"""

EDIT_FULL_NAME_PROMPT = """
✍️ Введите ваши фамилию и имя:
"""

EDIT_EMAIL_PROMPT = """
📧 Введите обновленную почту:
"""

EDIT_PASSWORD_PROMPT = """
🔑 Введите новый пароль:
"""

EDIT_AVATAR_PROMPT = """
📸 Загрузите ваше фото для профиля:
"""

FULL_NAME_SAVED_MESSAGE = """
✅ Новое имя и фамилия сохранены!
"""

EMAIL_SAVED_MESSAGE = """
✅ Новая почта сохранена!
"""

PASSWORD_SAVED_MESSAGE = """
✅ Новый пароль сохранен!
"""

AVATAR_SAVED_MESSAGE = """
✅ Новая аватарка успешно загружена!
"""

TOKEN_EXPIRED_MESSAGE = """
⚠️ Срок действия токена истек(
🔄 Повторите авторизацию! /auth
"""

AVATAR_UPLOAD_ERROR_MESSAGE = """
❌ Ошибка при загрузке фото: {error}
🔁 Повторите отправку!
"""

DATA_UPDATED_MESSAGE = """
✅ Данные обновлены

{new_user_data}
"""

NOT_AUTHORIZED_DELETE = """
🚫 <b>Вы не авторизованы.</b> Пожалуйста, повторите попытку позже.
"""

REGISTRATION_ERROR = (
    'Возникла ошибка при регистрации пользователя! 🚫'
)
AUTHORIZATION_ERROR = (
    'Ошибка при получении JWT-токена. Повторите авторизацию! 🚫'
)
AUTHORIZATION_SAVE_TOKEN_ERROR = """
🚫 <b>Ошибка при сохранении токена</b> в базу данных.

Повторите попытку позже.
"""
DELETE_ACCOUNT_ERROR = 'Ошибка при удалении аккаунта! 🚫'
SELECT_EDIT_FIELD_ERROR = 'Ошибка при выборе поля редактирования! 🚫'
START_EDIT_ERROR = 'Ошибка при редактировании! 🚫'
SAVE_FULL_NAME_ERROR = (
    'Ошибка при сохранении новых данных о имени и фамилии в БД 🚫'
)
SAVE_EMAIL_ERROR = 'Ошибка при сохранении новой почты в БД 🚫'
SAVE_PASSWORD_ERROR = 'Ошибка при сохранении нового пароля в БД 🚫'
EDIT_FINISH_ERROR = 'Ошибка при сохранении изменений аккаунта 🚫'
SAVE_AVATAR_ERROR = 'Ошибка при сохранении аватарки 🚫'


@clear_messages
@load_data_for_register_user
async def account_settings(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await send_tracked_message(
        await get_interaction(update),
        context,
        text=ACCOUNT_SETTINGS_MESSAGE,
        reply_markup=InlineKeyboardMarkup(ACCOUNT_SETTINGS_BUTTONS)
    )


@clear_messages
@load_data_for_register_user
async def load_account_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.delete()
    await send_tracked_message(
        update,
        context,
        text=LOAD_ACCOUNT_DATA_MESSAGE,
        reply_markup=InlineKeyboardMarkup(LOAD_ACCOUNT_DATA)
    )


@clear_messages
@load_data_for_register_user
async def check_account_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.delete()
    account = context.user_data['account']
    user_data = ACCOUNT_DATA_MESSAGE.format(
        name=account['name'],
        surname=account['surname'],
        email=account['email'],
        telegram_id=account['telegram_id'],
        chat_id=account['chat_id'],
        active='✅' if account['is_active'] else '❌',
        is_verified='✅' if account['is_verified'] else '❌',
        is_superuser='✅' if account['is_superuser'] else '❌',
        jwt_token=account['jwt_token'] if account.get('jwt_token') else '❌'
    )
    if user_avatar := account.get('media'):
        try:
            with open(user_avatar[-1]['path'], 'rb') as image_file:
                await send_tracked_photo(
                    update,
                    context,
                    caption=user_data,
                    photo=InputFile(image_file),
                    reply_markup=InlineKeyboardMarkup(
                        CHECK_ACCOUNT_DATA_BUTTONS
                    )
                )
        except Exception as error:
            print(f'Не удалось отправить аватар: {str(error)}')
    else:
        await send_tracked_message(
            update,
            context,
            text=user_data,
            reply_markup=InlineKeyboardMarkup(CHECK_ACCOUNT_DATA_BUTTONS)
        )


@clear_messages
async def start_registration(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик начала регистрации пользователя."""
    query = update.callback_query
    await query.answer()
    context.user_data['account'] = dict()
    await send_tracked_message(
        query,
        context,
        text=ASK_FULL_NAME
    )
    return REGISTRATION_FULL_NAME


@clear_messages
async def select_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_name = update.message.text
    await update.message.delete()
    if not await validate_full_name(update, context, full_name):
        return 'full_name'
    name, surname = full_name.split()
    context.user_data['account']['name'] = name
    context.user_data['account']['surname'] = surname
    await send_tracked_message(
        update,
        context,
        text=ASK_EMAIL
    )
    return REGISTRATION_EMAIL


@clear_messages
async def select_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entered_email = update.message.text.lower()
    await update.message.delete()
    if not await validate_email(update, context, entered_email):
        return 'email'
    context.user_data['account']['email'] = entered_email
    await send_tracked_message(
        update,
        context,
        text=ASK_PASSWORD.format(
            min=PASSWORD_MIN_LENGTH,
            max=PASSWORD_MAX_LENGTH
        )
    )
    return REGISTRATION_PASSWORD


@catch_error(REGISTRATION_ERROR, conv=True)
@clear_messages
async def select_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entered_password = update.message.text
    await update.message.delete()
    if not await validate_password(update, context, entered_password):
        return 'password'
    context.user_data['account']['password'] = entered_password
    context.user_data['account']['telegram_id'] = update.message.from_user.id
    context.user_data['account']['chat_id'] = str(update.message.chat.id)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            REGISTER_USER, json=context.user_data['account']
        ) as response:
            if response.status == HTTPStatus.CREATED:
                user = await response.json()
                await send_tracked_message(
                    update,
                    context,
                    text=REGISTRATION_SUCCESS
                )
                await send_tracked_message(
                    update,
                    context,
                    text=REGISTRATION_GREETING_TEMPLATE.format(
                        name=user['name'],
                        user_id=user['id']
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        FINISH_REGISTRATION_BUTTONS
                    )
                )
            else:
                detail = await response.json()
                await update.message.reply_text(detail)
    return ConversationHandler.END


@clear_messages
async def get_password_for_authorization(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await send_tracked_message(
        await get_interaction(update),
        context,
        text=ASK_PASSWORD_AUTH
    )
    return AUTH_AUTHORIZATION


@catch_error(AUTHORIZATION_ERROR, conv=True)
@clear_messages
@load_data_for_register_user
async def authorization(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if not context.user_data.get('account'):
        await send_tracked_message(
            update,
            context,
            text=NO_ACCOUNT_LOADED
        )
        return ConversationHandler.END
    entered_password = update.message.text
    await update.message.delete()
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
            USERS_REFRESH_ME,
            headers=get_headers(context),
            json=dict(
                jwt_token=dict(
                    access_token=context.user_data['account']['jwt_token']
                )
            )
        ) as response:
            if response.status == HTTPStatus.OK:
                await send_tracked_message(
                    update,
                    context,
                    text=AUTH_SUCCESS,
                    reply_markup=InlineKeyboardMarkup(
                        FINISH_AUTHORIZATION_BUTTONS
                    )
                )
                return ConversationHandler.END
            await update.message.reply_text(
                    AUTHORIZATION_SAVE_TOKEN_ERROR
                )
            return ConversationHandler.END
        return ConversationHandler.END


@clear_messages
async def get_password_for_delete_account(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await send_tracked_message(
        update,
        context,
        text=ASK_PASSWORD_FOR_DELETE
    )
    return DELETE_START_DELETE


@catch_error(DELETE_ACCOUNT_ERROR, conv=True)
@clear_messages
@load_data_for_register_user
async def delete_account(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    entered_password = update.message.text
    await update.message.delete()
    async with aiohttp.ClientSession() as session:
        if not await check_password(
            update, context,
            entered_password,
            context.user_data['account']['hashed_password']
        ):
            return DELETE_START_DELETE
        if not await check_authorization(update, context):
            return ConversationHandler.END
        async with session.delete(
            DELETE_USER_BY_ID.format(
                id=context.user_data['account']['id']
            ),
            headers=get_headers(context)
        ):
            context.user_data.pop('account')
            await send_tracked_message(
                update,
                context,
                text=DELETE_SUCCESS
            )
            return ConversationHandler.END


@clear_messages
async def get_password_for_edit_account(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['edit_account'] = dict()
    await send_tracked_message(
        update,
        context,
        text=START_EDIT_PASSWORD_PROMPT
    )
    return EDIT_CHOOSE_EDIT_FIELD


@catch_error(SELECT_EDIT_FIELD_ERROR, conv=True)
@clear_messages
@load_data_for_register_user
async def choose_edit_field(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    entered_password = update.message.text
    await update.message.delete()
    interaction = await get_interaction(update)
    if not await check_password(
        interaction,
        context,
        entered_password,
        context.user_data['account']['hashed_password']
    ):
        return EDIT_CHOOSE_EDIT_FIELD
    if not await check_authorization(interaction, context):
        return ConversationHandler.END
    await send_tracked_message(
        interaction,
        context,
        text=CHOOSE_EDIT_FIELD_PROMPT,
        reply_markup=InlineKeyboardMarkup(EDIT_BUTTONS)
    )
    return EDIT_START_EDIT_FIELD


@catch_error(START_EDIT_ERROR, conv=True)
@clear_messages
async def start_edit_field(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    field = query.data
    if field == EDIT_FULL_NAME_CALLBACK:
        await send_tracked_message(
            query,
            context,
            text=EDIT_FULL_NAME_PROMPT
        )
        return EDIT_SAVE_EDIT_FULL_NAME
    elif field == EDIT_EMAIL_CALLBACK:
        await send_tracked_message(
            query,
            context,
            text=EDIT_EMAIL_PROMPT
        )
        return EDIT_SAVE_EDIT_EMAIL
    elif field == EDIT_PASSWORD:
        await send_tracked_message(
            query,
            context,
            text=EDIT_PASSWORD_PROMPT
        )
        return EDIT_SAVE_EDIT_PASSWORD
    elif field == EDIT_ADD_AVATAR:
        await send_tracked_message(
            query,
            context,
            text=EDIT_AVATAR_PROMPT
        )
        return EDIT_SAVE_AVATAR


@catch_error(SAVE_FULL_NAME_ERROR)
@clear_messages
async def save_edit_full_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    full_name = update.message.text
    await update.message.delete()
    if not await validate_full_name(update, context, full_name):
        return EDIT_SAVE_EDIT_FULL_NAME
    name, surname = full_name.split()
    context.user_data['edit_account']['name'] = name
    context.user_data['edit_account']['surname'] = surname
    await send_tracked_message(
        update,
        context,
        text=FULL_NAME_SAVED_MESSAGE,
    )
    await send_tracked_message(
        update,
        context,
        text=CHOOSE_EDIT_FIELD_PROMPT,
        reply_markup=InlineKeyboardMarkup(EDIT_BUTTONS)
    )
    return EDIT_START_EDIT_FIELD


@catch_error(SAVE_EMAIL_ERROR, conv=True)
@clear_messages
async def save_edit_email(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    email = update.message.text
    await update.message.delete()
    if not await validate_email(update, context, email):
        return EDIT_SAVE_EDIT_EMAIL
    context.user_data['edit_account']['email'] = email
    await send_tracked_message(
        update,
        context,
        text=EMAIL_SAVED_MESSAGE
    )
    await send_tracked_message(
        update,
        context,
        text=CHOOSE_EDIT_FIELD_PROMPT,
        reply_markup=InlineKeyboardMarkup(EDIT_BUTTONS)
    )
    return EDIT_START_EDIT_FIELD


@catch_error(SAVE_PASSWORD_ERROR, conv=True)
@clear_messages
async def save_edit_password(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    password = update.message.text
    await update.message.delete()
    if not await validate_password(update, context, password):
        return EDIT_SAVE_EDIT_PASSWORD
    context.user_data['edit_account']['password'] = password
    await send_tracked_message(
        update,
        context,
        text=PASSWORD_SAVED_MESSAGE
    )
    await send_tracked_message(
        update,
        context,
        text=CHOOSE_EDIT_FIELD_PROMPT,
        reply_markup=InlineKeyboardMarkup(EDIT_BUTTONS)
    )
    return EDIT_START_EDIT_FIELD


@catch_error(SAVE_AVATAR_ERROR)
@clear_messages
async def save_avatar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not await validate_empty_photo(update, context):
        return EDIT_SAVE_AVATAR
    photo = update.message.photo[-1]
    await update.message.delete()
    file_id = photo.file_id
    tg_file = await context.bot.get_file(file_id)
    file_data = await tg_file.download_as_bytearray()
    async with aiohttp.ClientSession() as session:
        form = aiohttp.FormData()
        form.add_field(
            name='file',
            value=file_data,
            filename=f'{update.effective_user.id}.jpg',
            content_type='image/jpg'
        )
        async with session.post(
            ADD_NEW_AVATAR,
            data=form,
            headers=get_headers(context)
        ) as response:
            if response.status == HTTPStatus.UNAUTHORIZED:
                await send_tracked_message(
                    update,
                    context,
                    text=TOKEN_EXPIRED_MESSAGE
                )
                return ConversationHandler.END
            if response.status != HTTPStatus.OK:
                error_data = await response.json()
                await send_tracked_message(
                    update,
                    context,
                    text=AVATAR_UPLOAD_ERROR_MESSAGE.format(
                        error=error_data
                    )
                )
                return EDIT_ADD_AVATAR
            photo = await response.json()
    context.user_data['edit_account']['photo_id'] = photo['id']
    await send_tracked_message(
        update,
        context,
        text=AVATAR_SAVED_MESSAGE
    )
    await send_tracked_message(
        update,
        context,
        text=CHOOSE_EDIT_FIELD_PROMPT,
        reply_markup=InlineKeyboardMarkup(EDIT_BUTTONS)
    )
    return EDIT_START_EDIT_FIELD


@catch_error(EDIT_FINISH_ERROR)
@clear_messages
@load_data_for_register_user
async def finish_edit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    async with aiohttp.ClientSession() as session:
        async with session.patch(
            USERS_REFRESH_ME,
            headers=get_headers(context),
            json=context.user_data['edit_account']
        ) as response:
            new_user_data = await response.json()
            await send_tracked_message(
                query,
                context,
                text=DATA_UPDATED_MESSAGE.format(
                    new_user_data=USER_CARD.format(
                        name=new_user_data['name'],
                        surname=new_user_data['surname'],
                        telegram_id=new_user_data['telegram_id'],
                        email=new_user_data['email'],
                        jwt_token=new_user_data['jwt_token']['access_token']
                    )
                ),
                reply_markup=InlineKeyboardMarkup(
                    FINISH_EDIT_BUTTONS
                )
            )
            return ConversationHandler.END


def handlers_installer(
    application: ApplicationBuilder
) -> None:
    application.add_handler(
        CommandHandler('account_settings', account_settings)
    )
    application.add_handler(
        CallbackQueryHandler(
            account_settings, pattern=f'^{ACCOUNT_SETTINGS}$'
        )
    )
    application.add_handler(
        CommandHandler('account_data', check_account_data)
    )
    application.add_handler(
        CommandHandler('load_data', load_account_data)
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
            )
        ],
        states={
            AUTH_AUTHORIZATION: [
                MessageHandler(MESSAGE_HANDLERS, authorization)
            ],
            AUTH_GET_PASSWORD: [
                MessageHandler(
                    MESSAGE_HANDLERS, get_password_for_authorization
                )
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
            EDIT_SAVE_EDIT_EMAIL: [
                MessageHandler(MESSAGE_HANDLERS, save_edit_email)
            ],
            EDIT_SAVE_EDIT_PASSWORD: [
                MessageHandler(MESSAGE_HANDLERS, save_edit_password)
            ],
            EDIT_SAVE_AVATAR: [
                MessageHandler(PHOTO_HANDLERS, save_avatar)
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
