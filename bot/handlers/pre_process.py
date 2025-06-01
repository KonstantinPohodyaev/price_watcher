import aiohttp
from telegram import Update
from telegram.ext import ContextTypes

from bot.endpoints import GET_USER_BY_TELEGRAM_ID


def load_data_for_register_user(handler_func):
    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Декаратор, позволяющий подгружать данные о пользователе.
        
        Срабатывает перед выполнением основного хандлера handler_func.
        """
        if not context.user_data.get('account'):
            context.user_data['account'] = dict()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GET_USER_BY_TELEGRAM_ID, json=dict(
                    telegram_id=update.message.from_user.id
                )
            ) as response:
                user_data = await response.json()
                if user_data:
                    for field, value in user_data.items():
                        context.user_data['account'][field] = value
        return await handler_func(update, context)
    return wrapper
