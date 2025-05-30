from fastapi import APIRouter

from src.api.v1.endpoints import track_router, user_router, price_history_router

TRACK_TAGS = ['track']
PRICE_HISTORY_TAGS = ['price_history']


main_router = APIRouter()

main_router.include_router(user_router)
main_router.include_router(track_router, tags=TRACK_TAGS)
main_router.include_router(price_history_router, tags=PRICE_HISTORY_TAGS)
