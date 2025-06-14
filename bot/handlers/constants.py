from telegram.ext import filters
from telegram.constants import ParseMode

MESSAGE_HANDLERS = filters.TEXT & ~filters.COMMAND
PARSE_MODE = ParseMode.HTML
