import os

import aiohttp
from cryptography.fernet import Fernet
from telegram import Update
from telegram.ext import ContextTypes

from bot.endpoints import GET_USER_BY_TELEGRAM_ID
from bot.handlers.utils import get_interaction, get_telegram_id

fernet = Fernet(
    os.getenv(
        'JWT_SECRET_KEY',
        'A8zOVVp4FMb93RD03n0O25FwAYmTxmTQhF3kPBnLJ6E='
    )
)


def load_data_for_register_user(handler_func):
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Декаратор, позволяющий подгружать данные о пользователе.

        Срабатывает перед выполнением основного хандлера handler_func.
        """
        interaction = await get_interaction(update)
        if not context.user_data.get('account'):
            context.user_data['account'] = dict()
        telegram_id = get_telegram_id(interaction)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GET_USER_BY_TELEGRAM_ID,
                json=dict(telegram_id=telegram_id)
            ) as response:
                user_data = await response.json()
                if user_data:
                    jwt_token_data = user_data.pop('jwt_token')
                    if jwt_token_data:
                        access_token = fernet.decrypt(
                            jwt_token_data['access_token']
                        ).decode()
                        user_data['jwt_token'] = access_token
                    for field, value in user_data.items():
                        context.user_data['account'][field] = value
        return await handler_func(update, context)
    return wrapper


def clear_messages(handler_func):
    async def wrapper(update, context):
        """Проверка пользователя на аутентификацию."""
        interaction = await get_interaction(update)
        if not context.user_data.get('last_message_ids'):
            context.user_data['last_message_ids'] = list()
        else:
            for message_id in context.user_data['last_message_ids']:
                print(message_id)
                await context.bot.delete_message(
                    chat_id=interaction.message.chat.id,
                    message_id=message_id
                )
            context.user_data['last_message_ids'] = list()
        return await handler_func(update, context)
    return wrapper
