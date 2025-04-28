import os

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


DEFAULT_APP_TITLE = 'Price Watcher'
DEFAULT_APP_DESCRIPTION = 'Сервис для просмотра цен.'


load_dotenv()


class Settings(BaseSettings):
    database_url: str = os.getenv('DATABASE_URL')
    secret: str = os.getenv('SECRET')
    title: str = os.getenv('TITLE', DEFAULT_APP_TITLE)
    description: str = os.getenv('DESCRIPTION', DEFAULT_APP_DESCRIPTION)


settings = Settings()
