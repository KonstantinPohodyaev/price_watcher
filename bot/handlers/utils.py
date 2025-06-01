import aiohttp
from aiohttp import ClientSession
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from telegram import Update
from telegram.ext import ContextTypes

from bot.endpoints import GET_USER_BY_TELEGRAM_ID

password_hasher = PasswordHasher()


def check_password(
    entered_password: str, hashed_user_password: str
) -> bool:
    try:
        password_hasher.verify(
            hashed_user_password, entered_password
        )
        return True
    except VerifyMismatchError:
        return False


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
