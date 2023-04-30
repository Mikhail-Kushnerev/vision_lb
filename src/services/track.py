from functools import lru_cache
from http import HTTPStatus
from pathlib import Path
from uuid import UUID

import matplotlib.pyplot as plt
from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_session
from crud.factories import get_crud_by_client
from models import PointsModel
from schemes.track import Body, Point
from services.file import FileManager


class TrackService:
    def __init__(self, client):
        self._crud = get_crud_by_client(self.__class__)(PointsModel, client) # fabrica
        self._manager = FileManager()

    async def create_graph(self, points: Body) -> dict | str:
        try:
            await self._crud.create(points)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Не удалось создать!'
            )
        else:
            return "q"

    async def get_track_by_id(self, track_id: UUID) -> list[Point] | dict:
        try:
            points = await self._crud.get(track_id)
            #TODO: add exceptions
            if not points:
                raise SQLAlchemyError
        except SQLAlchemyError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Не удалось построить трэк!'
            )
        else:
            return points

    async def draw_track_on_img(self, track_id: UUID, image: UploadFile) -> Path:
        points = await self.get_track_by_id(track_id)
        path = await self._manager(image)

        img = plt.imread(path)
        plt.imshow(img)
        plt.plot([point.x for point in points], [point.y for point in points], 'o-')

        file_name = await self._manager.generate_name(track_id)
        plt.savefig(file_name)
        plt.close()

        return file_name


@lru_cache
def get_tack_service(
        client: AsyncSession = Depends(get_session)
):
    return TrackService(client)
