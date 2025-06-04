import aiohttp
from aiohttp import ClientSession
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from telegram import Update
from telegram.ext import ContextTypes

from bot.endpoints import GET_USER_BY_TELEGRAM_ID

password_hasher = PasswordHasher()


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
            'Для удаления аккаунта необходима авторизация'
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
