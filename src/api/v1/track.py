"""Модуль с API трэка"""

from uuid import UUID

from fastapi import APIRouter, UploadFile, Depends, File
from fastapi.responses import FileResponse

from schemes.track import BodySchema
from services.track import get_tack_service, TrackService

track_router = APIRouter()


@track_router.post(
    '/set-points',
    summary='Новый трэк',
    response_description='Трэк сохранен',
)
async def set_params(
        params: BodySchema,
        track_service: TrackService = Depends(get_tack_service)
):
    """
    API сохраняет параметры для указанного трэка.

    Args:
        params: параметры трэка (идентификатор и значения точек)

    Returns:
        Результат сохранения
    """
    return await track_service.create_track(params)


@track_router.post(
    '/plot',
    summary='Построение трэка',
    response_description='Трэк построен',
)
async def plot_track(
        id_: UUID,
        file: UploadFile = File(...),
        track_service: TrackService = Depends(get_tack_service)
) -> FileResponse:
    """
    API выстраивает заданный трэк на изображении

    Args:
        id_: идентификатор трэка
        file: файл для отрисовки

    Returns:
        Отрисованный трэк
    """
    drawed_track = await track_service.draw_track_on_img(id_, file)
    return FileResponse(drawed_track)
