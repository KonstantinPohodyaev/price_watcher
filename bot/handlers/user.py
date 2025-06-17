from http import HTTPStatus

import aiohttp
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardRemove, Update)
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ContextTypes, ConversationHandler,
                          MessageHandler, filters)

from bot.endpoints import (DELETE_USER_BY_ID, GET_JWT_TOKEN, REGISTER_USER,
                           USERS_REFRESH_ME, ADD_NEW_AVATAR)
from bot.handlers.buttons import REPLY_KEYBOARD
from bot.handlers.callback_data import (EDIT_EMAIL_CALLBACK,
                                        EDIT_FULL_NAME_CALLBACK, EDIT_PASSWORD,
                                        MENU, ACCOUNT_SETTINGS,
                                        EDIT_ADD_AVATAR)
from bot.handlers.constants import MESSAGE_HANDLERS, PARSE_MODE
from bot.handlers.pre_process import load_data_for_register_user, clear_messages
from bot.handlers.utils import (catch_error, check_authorization,
                                check_password, get_headers, get_interaction,
                                add_message_to_delete_list)
from bot.handlers.validators import (validate_email, validate_full_name,
                                     validate_password, validate_empty_photo)

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

USER_CARD = """
👤 <b>Полное имя:</b> {name} {surname}  
📧 <b>Почта:</b> <code>{email}</code>  
🆔 <b>Telegram ID:</b> <code>{telegram_id}</code>
🔐 <b>JWT:</b> <code>{jwt_token}</code>
"""

REGISTRATION_ERROR = (
    'Возникла ошибка при регистрации пользователя! 🚫'
)
AUTHORIZATION_ERROR = (
    'Ошибка при получении JWT-токена. Повторите регистрацию! 🚫'
)
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

EDIT_BUTTONS = [
    [
        InlineKeyboardButton(
            'Добавить фото', callback_data=EDIT_ADD_AVATAR
        )
    ],
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

@clear_messages
@load_data_for_register_user
async def account_settings(
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
    message = await interaction.message.reply_text(
        text=ACCOUNT_SETTINGS_MESSAGE,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=PARSE_MODE
    )
    add_message_to_delete_list(message, context)


@clear_messages
@load_data_for_register_user
async def load_account_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    buttons = [
        [
            InlineKeyboardButton('Меню 📦', callback_data=MENU)
        ]
    ]
    message = await update.message.reply_text(
        'Данные аккаунта успешно обновлены! ✅',
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    add_message_to_delete_list(message, context)


@clear_messages
@load_data_for_register_user
async def check_account_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    account = context.user_data['account']
    buttons = [
        [
            InlineKeyboardButton('Меню 📦', callback_data=MENU)
        ]
    ]
    message = await update.message.reply_text(
        text=ACCOUNT_DATA_MESSAGE.format(
            name=account['name'],
            surname=account['surname'],
            email=account['email'],
            telegram_id=account['telegram_id'],
            chat_id=account['chat_id'],
            active='✅' if account['is_active'] else '❌',
            is_verified='✅' if account['is_verified'] else '❌',
            is_superuser='✅' if account['is_superuser'] else '❌',
            jwt_token=account['jwt_token']
        ),
        parse_mode=PARSE_MODE,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    add_message_to_delete_list(message, context)


@clear_messages
async def start_registration(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик начала регистрации пользователя."""
    query = update.callback_query
    await query.answer()
    context.user_data['account'] = dict()
    message = await query.message.reply_text(
        'Укажите Ваше имя и фамилию через пробел: '
    )
    add_message_to_delete_list(message, context)
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
    message = await update.message.reply_text(
        'Укажите Вашу почту: '
    )
    add_message_to_delete_list(message, context)
    return REGISTRATION_EMAIL


@clear_messages
async def select_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entered_email = update.message.text
    await update.message.delete()
    if not await validate_email(update, context, entered_email):
        return 'email'
    context.user_data['account']['email'] = entered_email
    message = await update.message.reply_text(
        'Придумайте пароль: '
    )
    add_message_to_delete_list(message, context)
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
                message = await update.message.reply_text(
                    'Регистрация закончена!',
                    reply_markup=REPLY_KEYBOARD
                )
                add_message_to_delete_list(message, context)
                buttons = [
                    [
                        InlineKeyboardButton(
                            'Авторизация', callback_data='authorization'
                        )
                    ]
                ]
                message = await update.message.reply_text(
                    text=(
                        f'Привет, {user["name"]}! '
                        f'Вот твой id: {user["id"]}'
                    ),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                add_message_to_delete_list(message, context)
            else:
                detail = await response.json()
                await update.message.reply_text(detail)
    return ConversationHandler.END


@clear_messages
async def get_password_for_authorization(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        config = query
    else:
        config = update
    message = await config.message.reply_text(
        'Введите пароль от вашего аккаунта:'
    )
    add_message_to_delete_list(message, context)
    return AUTH_AUTHORIZATION


@catch_error(AUTHORIZATION_ERROR, conv=True)
@clear_messages
@load_data_for_register_user
async def authorization(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
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
            if response.status == 200:
                buttons = [
                    [
                        InlineKeyboardButton(
                            'Меню 📦', callback_data=MENU
                        )
                    ]
                ]
                message = await update.message.reply_text(
                    'Авторизация выполнена 🔐',
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                add_message_to_delete_list(message, context)
                return ConversationHandler.END
            await update.message.reply_text(
                    'Ошибка при сохранении нового токена в БД 🚫'
                )
            return ConversationHandler.END
        return ConversationHandler.END


@clear_messages
async def get_password_for_delete_account(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    message = await update.message.reply_text(
        '🔐 Введите пароль от вашего аккаунта:'
    )
    add_message_to_delete_list(message, context)
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
            return 'delete_account'
        if not await check_authorization(update, context):
            return ConversationHandler.END
        async with session.delete(
            DELETE_USER_BY_ID.format(
                id=context.user_data["account"]["id"]
            ),
            headers=get_headers(context)
        ):
            context.user_data.pop('account')
            message = await update.message.reply_text(
                'Ваш акккаунт удален!\n'
                'Вы можете зарегестрироваться снова - /start',
                reply_markup=ReplyKeyboardRemove()
            )
            add_message_to_delete_list(message, context)
            return ConversationHandler.END


@clear_messages
async def get_password_for_edit_account(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    context.user_data['edit_account'] = dict()
    message = await update.message.reply_text(
        'Введите пароль от вашего аккаунта:'
    )
    add_message_to_delete_list(message, context)
    return 'choose_edit_field'


@catch_error(SELECT_EDIT_FIELD_ERROR, conv=True)
@clear_messages
@load_data_for_register_user
async def choose_edit_field(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    entered_password = update.message.text
    await update.message.delete()
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
    message = await update.message.reply_text(
        'Выберите поле для редактирования ⏳\n'
        'После редактирования нажмите применить!',
        reply_markup=InlineKeyboardMarkup(EDIT_BUTTONS)
    )
    add_message_to_delete_list(message, context)
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
        message = await query.message.reply_text(
            'Введите ваши фамилию и имя:'
        )
        add_message_to_delete_list(message, context)
        return EDIT_SAVE_EDIT_FULL_NAME
    elif field == EDIT_EMAIL_CALLBACK:
        message = await query.message.reply_text(
            'Введите обновленную почту:'
        )
        add_message_to_delete_list(message, context)
        return EDIT_SAVE_EDIT_EMAIL
    elif field == EDIT_PASSWORD:
        message = await query.message.reply_text(
            'Введите новый пароль:'
        )
        add_message_to_delete_list(message, context)
        return EDIT_SAVE_EDIT_PASSWORD
    elif field == EDIT_ADD_AVATAR:
        message = await query.message.reply_text(
            'Загрузите ваше фото для профиля:'
        )
        add_message_to_delete_list(message, context)
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
    message = await update.message.reply_text(
        'Новое имя и фамилия сохранены!\n'
    )
    add_message_to_delete_list(message, context)
    message = await update.message.reply_text(
        'Выберите поле для редактирования ⏳',
        reply_markup=InlineKeyboardMarkup(EDIT_BUTTONS)
    )
    add_message_to_delete_list(message, context)
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
    message = await update.message.reply_text(
        'Новая почта сохранена!\n'
    )
    add_message_to_delete_list(message, context)
    message = await update.message.reply_text(
        'Выберите поле для редактирования ⏳',
        reply_markup=InlineKeyboardMarkup(EDIT_BUTTONS)
    )
    add_message_to_delete_list(message, context)
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
    message = await update.message.reply_text(
        'Новый пароль сохранен!\n'
    )
    add_message_to_delete_list(message, context)
    message = await update.message.reply_text(
        'Выберите поле для редактирования ⏳',
        reply_markup=InlineKeyboardMarkup(EDIT_BUTTONS)
    )
    add_message_to_delete_list(message, context)
    return EDIT_START_EDIT_FIELD


@catch_error(SAVE_AVATAR_ERROR)
@clear_messages
async def save_avatar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not validate_empty_photo(update):
        return EDIT_SAVE_AVATAR
    photo = update.message.photo[-1]
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
            if response.status != HTTPStatus.OK:
                error_data = await response.json()
                message = await update.message.reply_text(
                    f'Ошибка при загрузке фото: {error_data} '
                    'Повторите отправку!'
                )
                add_message_to_delete_list(message, context)
                return EDIT_ADD_AVATAR
            photo = await response.json()
    context.user_data['edit_account']['photo_id'] = photo['id']
    message = await update.message.reply_text(
        'Новая аватарка успешно загружена!\n'
    )
    add_message_to_delete_list(message, context)
    message = await update.message.reply_text(
        'Выберите поле для редактирования ⏳',
        reply_markup=InlineKeyboardMarkup(EDIT_BUTTONS)
    )
    add_message_to_delete_list(message, context)
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
            buttons=[
                [
                    InlineKeyboardButton(
                        'Назад', callback_data=ACCOUNT_SETTINGS
                    )
                ]
            ]
            message = await query.message.reply_text(
                text='Данные обновлены ✅\n' + 
                USER_CARD.format(
                    name=new_user_data['name'],
                    surname=new_user_data['surname'],
                    telegram_id=new_user_data['telegram_id'],
                    email=new_user_data['email'],
                    jwt_token=new_user_data['jwt_token']['access_token']
                ),
                reply_markup=InlineKeyboardMarkup(
                    buttons
                ),
                parse_mode=PARSE_MODE
            )
            add_message_to_delete_list(message, context)
            return ConversationHandler.END


def handlers_installer(
    application: ApplicationBuilder
) -> None:
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex('^Ваш аккаунт 📱$'),
            account_settings
        )
    )
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
            EDIT_SAVE_EDIT_EMAIL: [
                MessageHandler(MESSAGE_HANDLERS, save_edit_email)
            ],
            EDIT_SAVE_EDIT_PASSWORD: [
                MessageHandler(MESSAGE_HANDLERS, save_edit_password)
            ],
            EDIT_ADD_AVATAR: [
                MessageHandler(MESSAGE_HANDLERS, save_avatar)
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
