"""Модуль для работы с трэками."""

from functools import lru_cache
from http import HTTPStatus
from pathlib import Path
from uuid import UUID

import matplotlib.pyplot as plt
from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_session
from crud.base import BaseCRUD
from crud.factories import get_crud_by_client
from models import PointsModel
from schemes.track import BodySchema, PointSchema
from services.file import FileManager
from utils.constants import Answer


class TrackService:
    """Класс-обработчик трэков."""

    def __init__(self, client):
        """
        Метод инициализирует CRUD-объект и обработчки файлов.

        Args:
            client: сессия подключения к БД
        """
        self._crud: BaseCRUD = get_crud_by_client(self.__class__)(PointsModel, client)
        self._manager = FileManager()

    async def create_graph(self, points: BodySchema) -> dict | str:
        """
        Метод создания трэка.

        Args:
            points: параметры трэка (`id` и точки)

        Returns:
            Сообщение об успешном или неуспешном создании.
        """

        try:
            await self._crud.create(points)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=Answer.FAIL_CREATE_TRACK
            )
        else:
            return Answer.DONE_CREATE_TRACK

    async def get_track_by_id(self, track_id: UUID) -> list[PointSchema] | dict:
        """
        Метод возвращает точки трэка по его `id`.

        Args:
            track_id: идентификатор трэка.
        Returns:
            точки по осям Х и У
        """

        try:
            points = await self._crud.get(track_id)
            if not points:
                raise ValueError
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=Answer.NOT_EXIST_TRACK
            )
        else:
            return points

    async def draw_track_on_img(self, track_id: UUID, image: UploadFile) -> Path:
        """
        Метод строит заданный трэк на входном изображении

        Args:
            track_id: идентификатор трэка
            image: входное изображение

        Returns:
            Путь до нарисованного трэка
        """

        points = await self.get_track_by_id(track_id)
        path = await self._manager.save(image)

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
