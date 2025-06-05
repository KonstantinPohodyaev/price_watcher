from decimal import Decimal
import re

import aiohttp
from telegram import Update
from telegram.ext import ContextTypes

from bot.endpoints import GET_USER_BY_EMAIL


VALIDATE_FULL_NAME_PATTERN = r'^[A-ZА-ЯЁa-zа-яё]+ [A-ZА-ЯЁa-zа-яё]+$'
FULL_NAME_PATTERN_ERROR = (
    'Неверный формат ввода имени и фамилии 🚫\n'
    'Вы указали {current}\n'
    'Попробуйте еще раз:'
)

EMAIL_PATTERN = r'^[A-Za-z0-9._%+-]+@(mail|gmail|yandex)\.(ru|com)$'
WRONG_EMAIL_PATTERN_ERROR = (
    'Введенный вариант почты {current} '
    'содержит недопустимые символы. 🚫\n'
    'Придумайте почту еще раз!'
)
NOT_UNIQUE_EMAIL_ERROR = (
    'Пользователь с email {current} уже существует. 🚫\n'
    'Придумайте новый'
)

PASSWORD_PATTERN = r'^\d+$'
PASSWORD_MIN_LENGTH = 3
PASSWORD_MAX_LENGTH = 6
WRONG_PASSWORD_LENGTH_ERROR = (
    'Пароль должен иметь длину не менее {min} '
    'и не более {max}. 🚫\n'
    'Ваша длина: {current}.\n'
    'Введите пароль еще раз:'
)
WRONG_PASSWORD_PATTERN_ERROR = (
    'Пароль должен содержать только цифры от 1 до 9 🚫'
)

VALIDATE_FULL_NAME_ERROR = 'Недопустимый формат ввода имени и фамилии.'


async def validate_full_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    full_name: str
) -> bool:
    """Проверяет формат ввода имени и фамилии."""
    if not bool(
        re.match(
            VALIDATE_FULL_NAME_PATTERN,
            full_name
        )
    ):
        await update.message.reply_text(
            FULL_NAME_PATTERN_ERROR.format(current=full_name)
        )
        return False
    return True


async def validate_email(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    email: str
) -> bool:
    """Проверка валидности почты."""
    if not bool(
        re.match(
            EMAIL_PATTERN,
            email
        )
    ):
        await update.message.reply_text(
            WRONG_EMAIL_PATTERN_ERROR.format(current=email)
        )
        return False
    async with aiohttp.ClientSession() as session:
        async with session.post(
            GET_USER_BY_EMAIL,
            json=dict(email=email)
        ) as response:
            user_data = await response.json()
            if user_data:
                await update.message.reply_text(
                    NOT_UNIQUE_EMAIL_ERROR.format(
                        current=email
                    )
                )
                return False
    return True


async def validate_password(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    password: str
) -> bool:
    """
    Проверка валидности пароля.
    ________________________________
    - Требования к валидации зависят от продакшена.
    """
    if not bool(
        re.match(
            PASSWORD_PATTERN,
            password
        )
    ):
        await update.message.reply_text(WRONG_PASSWORD_PATTERN_ERROR)
        return False
    elif not PASSWORD_MIN_LENGTH < len(password) < PASSWORD_MAX_LENGTH:
        await update.message.reply_text(
            WRONG_PASSWORD_LENGTH_ERROR.format(
                min=PASSWORD_MIN_LENGTH,
                max=PASSWORD_MAX_LENGTH,
                current=len(password)
            )
        )
        return False
    return True


# async def validate_price(
#     update: Update,
#     context: ContextTypes.DEFAULT_TYPE,
#     price: str
# ) -> bool:
#     price = Decimal(price)
#     if price < Decimal('0'):
#         await 
