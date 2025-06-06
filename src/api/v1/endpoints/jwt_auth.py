import aiohttp
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.jwt_auth import jwt_token_crud
from src.database.db import get_async_session
from src.schemas.user import UserRead


router = APIRouter()
