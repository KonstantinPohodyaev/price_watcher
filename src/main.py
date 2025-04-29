from dotenv import load_dotenv
from fastapi import FastAPI

from src.api.v1.routers import main_router
from src.core.config import settings

load_dotenv()


app = FastAPI(
    title=settings.title,
    description=settings.description
)
app.router.include_router(main_router)
