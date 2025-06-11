import aiohttp

from bot.endpoints import USERS_TRACKS


async def check_prices_and_notify_users():
    async with aiohttp.ClientSession() as session:
        async with session.get(USERS_TRACKS) as response:
            tracks = await response.json()
            for track in tracks:
                