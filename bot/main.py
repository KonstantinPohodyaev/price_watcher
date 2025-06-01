import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

from bot.handlers import base_installer_handlers

load_dotenv()


def main():
    application = ApplicationBuilder().token(
        os.getenv('TELEGRAM_BOT_TOKEN')
    ).build()
    base_installer_handlers(application)
    application.run_polling()


if __name__ == '__main__':
    main()
