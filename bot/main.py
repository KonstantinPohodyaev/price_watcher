import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

from bot.handlers import (base_installer_handlers, track_handler_installer,
                          user_installer_handlers)


load_dotenv()


scheduler = AsyncIOScheduler()


def main():
    application = ApplicationBuilder().token(
        os.getenv('TELEGRAM_BOT_TOKEN')
    ).build()
    base_installer_handlers(application)
    user_installer_handlers(application)
    track_handler_installer(application)
    application.run_polling()


if __name__ == '__main__':
    main()
