"""Модуль подключения API"""

from fastapi import APIRouter

from .v1.track import track_router

main_router = APIRouter()
main_router.include_router(
    track_router,
    prefix='/api/v1',
    tags=['Track plot']
)
