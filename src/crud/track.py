"""Модуль CRUD для треков."""

from uuid import UUID

from sqlalchemy import select

from schemes.track import PointSchema, BodySchema
from .base import BaseCRUD


class TrackCRUD(BaseCRUD):

    async def get(self, obj_id: UUID) -> list[PointSchema]:

        query = (
            select(self._model)
            .where(self._model.track_id == obj_id)
        )
        result = await self._client.execute(query)

        return [PointSchema(x=item.point_X, y=item.point_Y) for item in result.scalars()]

    async def create(self, params: BodySchema) -> None:
        points = params.points
        objects = []
        for point in points:
            item = self._model(track_id=params.track_id, point_X=point.x, point_Y=point.y)
            objects.append(item)
        else:
            self._client.add_all(objects)
            await self._client.commit()
