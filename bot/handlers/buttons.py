from telegram import ReplyKeyboardMarkup

MAIN_REPLY_BUTTONS = ['Меню 🔥', 'Авторизация 🔐', 'Ваш аккаунт 📱']

REPLY_KEYBOARD = ReplyKeyboardMarkup(
    [MAIN_REPLY_BUTTONS],
    resize_keyboard=True
)
