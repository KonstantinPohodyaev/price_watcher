from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CallbackQueryHandler, CommandHandler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Привет! Я KartPriceWatcherBot! Чем тебе помочь?'
    )


def handlers_installer(
    application: ApplicationBuilder
) -> None:
    application.add_handler(
        CommandHandler('start', start)
    )
