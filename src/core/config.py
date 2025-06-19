import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

DEFAULT_APP_TITLE = 'Price Watcher'
DEFAULT_APP_DESCRIPTION = 'Сервис для просмотра цен.'


load_dotenv()

UPLOAD_DIR = 'media'
STATIC_DIR = '/media'


class Settings(BaseSettings):
    db_dialect: str = os.getenv('DB_DIALECT')
    db_driver: str = os.getenv('DB_DRIVER')
    db_name: str = os.getenv('DB_NAME')
    secret: str = os.getenv('SECRET')
    title: str = os.getenv('TITLE', DEFAULT_APP_TITLE)
    description: str = os.getenv('DESCRIPTION', DEFAULT_APP_DESCRIPTION)
    first_superuser_email: str = os.getenv('FIRST_SUPERUSER_EMAIL')
    first_superuser_password: str = os.getenv('FIRST_SUPERUSER_PASSWORD')

    @property
    def database_url(self):
        return (
            f'{self.db_dialect}+{self.db_driver}:'
            f'///{self.db_name}'
        )


settings = Settings()
