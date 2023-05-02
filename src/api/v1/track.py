"""Модуль с API трека"""

from uuid import UUID

from fastapi import APIRouter, UploadFile, Depends, File, Form

from schemes.track import BodySchema
from services.track import get_tack_service, TrackService

track_router = APIRouter()


@track_router.post(
    '/set-points',
    summary='Новый трек',
    response_description='трек сохранен',
)
async def set_params(
        params: BodySchema,
        track_service: TrackService = Depends(get_tack_service)
):
    """
    API сохраняет параметры для указанного трека.

    Args:
        params: параметры трека (идентификатор и значения точек)

    Returns:
        Результат сохранения
    """
    return await track_service.create_track(params)


@track_router.post(
    '/plot',
    summary='Построение трека',
    response_description='трек построен'
)
async def plot_track(
        track_id: UUID = Form(...),
        image: UploadFile = File(...),
        track_service: TrackService = Depends(get_tack_service)
):
    """
    API выстраивает заданный трек на изображении

    Args:
        track_id: идентификатор трека
        image: файл для отрисовки

    Returns:
        Отрисованный трек
    """
    return await track_service.draw_track_on_img(track_id, image)
