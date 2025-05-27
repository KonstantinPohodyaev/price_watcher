PROTOCOL = 'http'
DOMEN = '127.0.0.1:8000'


GET_USER_BY_TELEGRAM_ID = f'{PROTOCOL}://{DOMEN}/users/check-telegram-id'
REGISTER_USER = f'{PROTOCOL}://{DOMEN}/auth/register'