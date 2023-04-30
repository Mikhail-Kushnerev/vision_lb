from fastapi import APIRouter

from .v1.track import graph_router

main_router = APIRouter()
main_router.include_router(
    graph_router,
    prefix='/api/v1',
    tags=['Graph plot']
)
