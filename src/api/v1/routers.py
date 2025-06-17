from fastapi import APIRouter

from src.api.v1.endpoints import (price_history_router, track_router,
                                  user_router, media_router)

TRACK_TAGS = ['track']
PRICE_HISTORY_TAGS = ['price_history']

MEDIA_PREFIX = '/media'
MEDIA_TAGS = ['media']


main_router = APIRouter()

main_router.include_router(
    user_router
)
main_router.include_router(
    track_router, tags=TRACK_TAGS
)
main_router.include_router(
    price_history_router, tags=PRICE_HISTORY_TAGS
)
main_router.include_router(
    media_router, prefix=MEDIA_PREFIX, tags=MEDIA_TAGS
)
