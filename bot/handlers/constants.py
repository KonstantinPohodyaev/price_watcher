from telegram.constants import ParseMode
from telegram.ext import filters

MESSAGE_HANDLERS = filters.TEXT & ~filters.COMMAND
PHOTO_HANDLERS = filters.PHOTO
PARSE_MODE = ParseMode.HTML
