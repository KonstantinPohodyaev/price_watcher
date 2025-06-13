import os
import re

from aiohttp import ClientSession
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.fernet import Fernet
from telegram import (CallbackQuery, InlineKeyboardButton,
                      InlineKeyboardMarkup, Update)
from telegram.ext import ContextTypes, ConversationHandler

from bot.endpoints import GET_USER_BY_TELEGRAM_ID
from bot.handlers.callback_data import CHECK_HISTORY

password_hasher = PasswordHasher()

fernet = Fernet(
    os.getenv(
        'JWT_SECRET_KEY',
        'A8zOVVp4FMb93RD03n0O25FwAYmTxmTQhF3kPBnLJ6E='
    )
)

# Вспомогательные утилиты.
def catch_error(error_message: str, conv=False):
    """Добавляет хандлерам try-except конструкцию."""
    def decorator(handler):
        async def wrapper(
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
            *args, **kwargs
        ):
            try:
                return await handler(update, context, *args, **kwargs)
            except Exception as error:
                interaction = await get_interaction(update)
                await interaction.message.reply_text(error_message)
                print(str(error))
                if conv:
                    return ConversationHandler.END
        return wrapper
    return decorator


def get_telegram_id(interaction: Update | CallbackQuery):
    """Находит телеграм id пользователя."""
    if isinstance(interaction, Update):
        return interaction.message.from_user.id
    return interaction.from_user.id


def add_message_to_delete_list(message, context: ContextTypes.DEFAULT_TYPE):
    """Добавляет сообщение в очередь на удаление."""
    if not context.user_data.get('last_message_ids'):
        context.user_data['last_message_ids'] = list()
    context.user_data['last_message_ids'].append(message.message_id)


async def check_password(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    entered_password: str,
    hashed_user_password: str
) -> bool:
    """Проверяет, совпадает ли введенный пароль с БД."""
    try:
        password_hasher.verify(
            hashed_user_password, entered_password
        )
        return True
    except VerifyMismatchError:
        await update.message.reply_text(
            'Вы ввели неправильный пароль 🚫\n'
            'Попробуйте еще раз.'
        )
        return False


async def check_authorization(
    interaction: Update | CallbackQuery,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Проверяет, авторизаван ли пользователь."""
    if not context.user_data.get('account', {}).get('jwt_token'):
        await interaction.message.reply_text(
            'Для совершения этой операции необходима авторизация /auth ⚠️'
        )
        return False
    return True


async def load_user_data(
    session: ClientSession,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """Загрузка пользовательский данных (для тестирования)."""
    async with session.post(
            GET_USER_BY_TELEGRAM_ID, json=dict(
            telegram_id=update.message.from_user.id
        )
    ) as response:
        user_data = await response.json()
        if user_data:
            for field, value in user_data.items():
                context.user_data['account'][field] = value


def escape_markdown_v2(text: str) -> str:
    """
    Экранирует спецсимволы MarkdownV2, чтобы избежать ошибок Telegram.
    """
    return re.sub(r'([\\_*[\]()~`>#+\-=|{}.!])', r'\\\1', text)


async def get_interaction(update: Update) -> Update | CallbackQuery:
    """Функция для определения действия с пользователем."""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        return query
    elif update.message:
        return update


def get_headers(
    context: ContextTypes.DEFAULT_TYPE
) -> dict[str, str]:
    """Собирает заголовок для прохождения авторизации."""
    return dict(
        Authorization=(
            f'Bearer {context.user_data["account"]["jwt_token"]}'
        )
    )


def decode_jwt_token(encoded_jwt_token):
    decoded_jwt_token = fernet.decrypt(encoded_jwt_token.encode())
    return decoded_jwt_token.decode()


# Утилиты для работы с клавиатурами.
def get_track_keyboard(track_id: int) -> list[InlineKeyboardButton]:
    """Собирает кнопки для экземпляра Track."""
    return [
        [
            InlineKeyboardButton(
                'Изменить ⚡',
                callback_data=f'track_refresh_target_price_{track_id}'
            ),
            InlineKeyboardButton(
                'Удалить ❌',
                callback_data=f'track_delete_{track_id}'
            )
        ],
        [
            InlineKeyboardButton(
                'Посмотреть историю 🛍️',
                callback_data=f'{CHECK_HISTORY}_{track_id}'
            )
        ]
    ]
