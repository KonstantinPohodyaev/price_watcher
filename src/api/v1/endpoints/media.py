import os

from fastapi import APIRouter, status, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.media import MediaDB, MediaCreate
from src.database.db import get_async_session
from src.crud.user import user_crud
from src.crud.media import media_crud
from src.models.user import User
from src.models.media import Media
from src.core.user import current_user


router = APIRouter()

UPLOAD_DIR = 'media'


@router.post(
    '/upload-avatar/{user_id}',
    response_model=MediaDB,
    status_code=status.HTTP_200_OK
)
async def upload_media(
    file: UploadFile,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    filename = f'{user.telegram_id}_{file.filename}'
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, 'wb') as new_file:
        new_file.write(await file.read())
    return await media_crud.create(
        MediaCreate(
            user_id=user.id,
            filename=filename,
            path=file_path
        ),
        session
    )
