from uuid import UUID

from fastapi import APIRouter, UploadFile, Depends, File
from fastapi.responses import FileResponse

from schemes.track import Body
from services.track import get_tack_service, TrackService

graph_router = APIRouter()


@graph_router.post(
    '/set-points',
    # status_code=204
)
async def set_params(
        params: Body,
        track_service: TrackService = Depends(get_tack_service)
):
    return await track_service.create_graph(params)


@graph_router.post(
    '/plot'
)
async def plot_graph(
        id_: UUID,
        file: UploadFile = File(...),
        track_service: TrackService = Depends(get_tack_service)
) -> FileResponse:
    drawed_track = await track_service.draw_track_on_img(id_, file)
    return FileResponse(drawed_track)
