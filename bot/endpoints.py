PROTOCOL = 'http'
DOMEN = '127.0.0.1:8000'


GET_USER_BY_TELEGRAM_ID = f'{PROTOCOL}://{DOMEN}/users/check-telegram-id'
GET_USER_BY_EMAIL = f'{PROTOCOL}://{DOMEN}/users/check-email'
REGISTER_USER = f'{PROTOCOL}://{DOMEN}/auth/register'
GET_JWT_TOKEN = f'{PROTOCOL}://{DOMEN}/auth/jwt/login'
USERS_ENDPOINT = f'{PROTOCOL}://{DOMEN}/users'
USERS_GET_ME = f'{PROTOCOL}://{DOMEN}/users/me'
USERS_ME_REFRESH = f'{PROTOCOL}://{DOMEN}/users/me/refresh'

USERS_TRACKS = f'{PROTOCOL}://{DOMEN}/tracks'
USERS_TRACKS_BY_ID = f'{PROTOCOL}://{DOMEN}/tracks/{{id}}'
CREATE_NEW_TRACK = f'{PROTOCOL}://{DOMEN}/tracks'
