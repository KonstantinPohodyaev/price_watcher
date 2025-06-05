from telegram.ext import filters


MESSAGE_HANDLERS = filters.TEXT & ~filters.COMMAND
PARSE_MODE = 'HTML'