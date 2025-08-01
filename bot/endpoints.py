import os


PROTOCOL = os.getenv('PROTOCOL', 'http')
API_CONTAINER = os.getenv('API_CONTAINER', 'api')
API_PORT = os.getenv('API_PORT', '8000')
DOMEN = f'{API_CONTAINER}:{API_PORT}'


# Эндпоинты User
GET_USER_BY_TELEGRAM_ID = f'{PROTOCOL}://{DOMEN}/users/check-telegram-id'
GET_USER_BY_EMAIL = f'{PROTOCOL}://{DOMEN}/users/check-email'
REGISTER_USER = f'{PROTOCOL}://{DOMEN}/auth/register'
GET_JWT_TOKEN = f'{PROTOCOL}://{DOMEN}/auth/jwt/login'
DELETE_USER_BY_ID = f'{PROTOCOL}://{DOMEN}/users/{{id}}'
USERS_GET_ME = f'{PROTOCOL}://{DOMEN}/users/me'
USERS_REFRESH_ME = f'{PROTOCOL}://{DOMEN}/users/me/refresh'

# Эндпоинты Track
USERS_TRACKS = f'{PROTOCOL}://{DOMEN}/tracks'
USERS_TRACKS_BY_ID = f'{PROTOCOL}://{DOMEN}/tracks/{{id}}'
CREATE_NEW_TRACK = f'{PROTOCOL}://{DOMEN}/tracks'
GET_TRACK_BY_ARTICLE_AND_MARKETPLACE = (
    f'{PROTOCOL}://{DOMEN}/tracks/{{marketplace}}/{{article}}'
)
DELETE_TRACK_BY_ID = f'{PROTOCOL}://{DOMEN}/tracks/{{id}}'
UPDATE_TRACK_BY_ID = f'{PROTOCOL}://{DOMEN}/tracks/{{id}}'
REFRESH_DATA_FOR_EXISTEN_TRACK = f'{PROTOCOL}://{DOMEN}/tracks/refresh/{{id}}'

# Эндпоинты PriceHistory
GET_TRACKS_PRICE_HISTORY = f'{PROTOCOL}://{DOMEN}/price-history/{{track_id}}'
ADD_ENTRY_ABOUT_TRACK = f'{PROTOCOL}://{DOMEN}/price-history/{{track_id}}'

# Эндпоинты Media
GET_USER_MEDIA = f'{PROTOCOL}://{DOMEN}/media/avatar/{{media_id}}'
ADD_NEW_AVATAR = f'{PROTOCOL}://{DOMEN}/media/upload-avatar'
