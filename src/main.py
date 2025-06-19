import os
from contextlib import asynccontextmanager
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.v1.routers import main_router
from src.core.config import STATIC_DIR, UPLOAD_DIR, settings
from src.core.init_db import create_first_superuser

load_dotenv()

UPLOAD_DIR = 'media'
STATIC_DIR = '/media'
os.makedirs(UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f'Приложение запущено! Дата: {datetime.now()}')
    await create_first_superuser()
    yield
    print(f'Приложение остановлено! Дата: {datetime.now()}')


app = FastAPI(
    title=settings.title,
    description=settings.description,
    lifespan=lifespan
)
app.router.include_router(main_router)
app.mount(STATIC_DIR, StaticFiles(directory=UPLOAD_DIR), name='media')
