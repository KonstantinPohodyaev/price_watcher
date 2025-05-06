import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

DEFAULT_APP_TITLE = 'Price Watcher'
DEFAULT_APP_DESCRIPTION = 'Сервис для просмотра цен.'


load_dotenv()


class Settings(BaseSettings):
    database_url: str = os.getenv('DATABASE_URL')
    secret: str = os.getenv('SECRET')
    title: str = os.getenv('TITLE', DEFAULT_APP_TITLE)
    description: str = os.getenv('DESCRIPTION', DEFAULT_APP_DESCRIPTION)
    first_superuser_email: str = os.getenv('FIRST_SUPERUSER_EMAIL')
    first_superuser_password: str = os.getenv('FIRST_SUPERUSER_PASSWORD')

    class Config:
        env_file = '.env'


settings = Settings()
