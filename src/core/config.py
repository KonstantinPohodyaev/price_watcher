import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

DEFAULT_APP_TITLE = 'Price Watcher'
DEFAULT_APP_DESCRIPTION = 'Сервис для просмотра цен.'


load_dotenv()

UPLOAD_DIR = 'media'
STATIC_DIR = '/media'


class Settings(BaseSettings):
    db_dialect: str
    db_driver: str
    secret: str
    title: str = DEFAULT_APP_TITLE
    description: str = DEFAULT_APP_DESCRIPTION
    first_superuser_email: str
    first_superuser_password: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: str
    postgres_host: str


    @property
    def database_url(self):
        return (
            f'{self.db_dialect}+{self.db_driver}://'
            f'{self.postgres_user}:{self.postgres_password}@'
            f'{self.postgres_host}:{self.postgres_port}'
            f'/{self.postgres_db}'
        )


settings = Settings()
print(settings.database_url)