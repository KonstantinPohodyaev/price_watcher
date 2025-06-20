import os
import uuid

import aiofiles
from fastapi import APIRouter, Depends, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import UPLOAD_DIR
from src.core.user import current_user
from src.crud.media import media_crud
from src.crud.user import user_crud
from src.database.db import get_async_session
from src.models.media import Media
from src.models.user import User
from src.schemas.media import MediaCreate, MediaDB

router = APIRouter()


@router.post(
    '/upload-avatar',
    response_model=MediaDB,
    status_code=status.HTTP_200_OK
)
async def upload_media(
    file: UploadFile,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    ext = os.path.splitext(file.filename)[1]
    filename = f'{user.telegram_id}_{uuid.uuid4().hex}{ext}'
    file_path = os.path.join(UPLOAD_DIR, filename)
    async with aiofiles.open(file_path, 'wb') as new_file:
        await new_file.write(await file.read())
    file_url = request.url_for(UPLOAD_DIR, path=filename)
    return await media_crud.create(
        MediaCreate(
            user_id=user.id,
            filename=filename,
            url=str(file_url),
            path=file_path
        ),
        session
    )


@router.get(
    '/avatar/{media_id}',
    response_model=MediaDB,
    status_code=status.HTTP_200_OK
)
async def get_user_avatar(
    media_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    return await media_crud.get(media_id, session)
