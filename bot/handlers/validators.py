import re

import aiohttp

from bot.endpoints import GET_USER_BY_EMAIL


VALIDATE_FULL_NAME_PATTERN = '^[A-ZА-ЯЁa-zа-яё]+ [A-ZА-ЯЁa-zа-яё]+$'
VALIDATE_FULL_NAME_ERROR = 'Недопустимый формат ввода имени и фамилии.'


def validate_full_name(
    full_name: str
) -> None:
    """Проверяет формат ввода имени и фамилии."""
    return bool(
        re.match(
            VALIDATE_FULL_NAME_PATTERN,
            full_name
        )
    )


async def check_unique_email(
    email: str,
):
    """Проверяет уникальность введенного email."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            GET_USER_BY_EMAIL,
            json=dict(email=email)
        ) as response:
            user_data = await response.json()
            return user_data
