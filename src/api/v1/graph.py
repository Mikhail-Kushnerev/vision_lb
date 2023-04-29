from uuid import UUID

from fastapi import APIRouter, UploadFile, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import async_session, get_session
from schemes.graph import PointsSchema

graph_router = APIRouter(prefix='/graphic')


@graph_router.post(
    '/set-points'
)
async def set_matrix(
        params: PointsSchema,
        session: AsyncSession = Depends(get_session)
):
    return 'Done!'


@graph_router.get(
    '/plot'
)
async def create_file(
        id: UUID,
        file: UploadFile,
        session: AsyncSession = Depends(get_session)
) -> FileResponse:
    # {'filename': file.filename}
    return FileResponse