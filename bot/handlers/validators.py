import re
from decimal import Decimal

import aiohttp
from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes

from bot.endpoints import GET_USER_BY_EMAIL
from bot.handlers.utils import send_tracked_message

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

PRICE_PATTERN = r'^\d+(\.\d{1,2})?$'
PRICE_PATTERN_ERROR = (
    'Цена содержит недопустимые символы!\n'
    'Введите ещё раз!'
)
PRICE_VALUE_ERROR = (
    'Цена не может быть меньше 0!\n'
    'Введите ещё раз!'
)

MARKETPLACES = ['wildberries', 'ozon']
MARKETPLACE_NOT_ALLOWED_ERROR = (
    'К сожалению Ваш маркетплэйс {current_marketplace} мы обработать '
    'не можем 😱\n'
    'Выберите'
)
EMPTY_PHOTO_ERROR = 'Пожалуйста, загрузите фото! 😱'


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
        await send_tracked_message(
            update,
            context,
            text=FULL_NAME_PATTERN_ERROR.format(current=full_name)
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
        await send_tracked_message(
            update,
            context,
            text=WRONG_EMAIL_PATTERN_ERROR.format(current=email)
        )
        return False
    async with aiohttp.ClientSession() as session:
        async with session.post(
            GET_USER_BY_EMAIL,
            json=dict(email=email)
        ) as response:
            user_data = await response.json()
            if user_data:
                await send_tracked_message(
                    update,
                    context,
                    text=NOT_UNIQUE_EMAIL_ERROR.format(current=email)
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
        await send_tracked_message(
            update,
            context,
            text=WRONG_PASSWORD_PATTERN_ERROR
        )
        return False
    elif not PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH:
        await send_tracked_message(
            update,
            context,
            text=WRONG_PASSWORD_LENGTH_ERROR.format(
                min=PASSWORD_MIN_LENGTH,
                max=PASSWORD_MAX_LENGTH,
                current=len(password)
            )
        )
        return False
    return True


async def validate_price(
    interaction: Update | CallbackQuery,
    context: ContextTypes.DEFAULT_TYPE,
    price: str
) -> bool:
    """Валидатор для цены"""
    str_price = price.strip().replace(',', '.')
    if not re.match(PRICE_PATTERN, str_price):
        await send_tracked_message(
            interaction,
            context,
            text=PRICE_PATTERN_ERROR
        )
        return False
    elif Decimal(str_price) < 0:
        await send_tracked_message(
            interaction,
            context,
            text=PRICE_VALUE_ERROR
        )
        return False
    return str_price


async def validate_empty_photo(
    interaction: Update | CallbackQuery,
    context: ContextTypes.DEFAULT_TYPE
) -> bool:
    if not interaction.message.photo:
        await send_tracked_message(
            interaction,
            context,
            text=EMPTY_PHOTO_ERROR
        )
        return False
    return True
