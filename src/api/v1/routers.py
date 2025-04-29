from fastapi import APIRouter

from src.api.v1.endpoints import track_router, user_router

TRACK_TAGS = ['track']


main_router = APIRouter()

main_router.include_router(user_router)
main_router.include_router(track_router, tags=TRACK_TAGS)
