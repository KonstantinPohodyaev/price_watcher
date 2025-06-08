import re

from aiohttp import ClientSession
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from telegram import CallbackQuery, Message, Update
from telegram.ext import ContextTypes

from bot.endpoints import GET_USER_BY_TELEGRAM_ID

password_hasher = PasswordHasher()


def catch_error(error_message: str):
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
        return wrapper
    return decorator


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
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Проверяет, авторизаван ли пользователь."""
    if not context.user_data['account'].get('jwt_token'):
        await update.message.reply_text(
            'Для совершения этой операции необходима авторизация /auth ⚠️'
        )
        return False
    return True


async def load_user_data(
    session: ClientSession,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
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
    return dict(
        Authorization=(
            f'Bearer {context.user_data["account"]["jwt_token"]}'
        )
    )
