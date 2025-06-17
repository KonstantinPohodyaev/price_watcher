from telegram.ext import filters
from telegram.constants import ParseMode

MESSAGE_HANDLERS = filters.TEXT & ~filters.COMMAND
PHOTO_HANDLERS = filters.PHOTO
PARSE_MODE = ParseMode.HTML
