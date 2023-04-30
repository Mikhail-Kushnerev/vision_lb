from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from schemes.track import Point, Body
from .base import BaseCRUD


class GraphCRUD(BaseCRUD):

    async def get(self, obj_id: UUID) -> list[Point]:

        query = (
            select(self._model)
            .where(self._model.graph_id == obj_id)
        )
        result = await self._client.execute(query)

        return [Point(x=item.point_X, y=item.point_Y) for item in result.scalars()]

    async def create(self, params: Body) -> None:
        obj = jsonable_encoder(params)
        track_id, points = obj.get('graph_id'), obj.get('points')
        objects = []
        for point in points:
            item = self._model(graph_id=track_id, point_X=point.get('x'), point_Y=point.get('y'))
            objects.append(item)
        else:
            self._client.add_all(objects)
            await self._client.commit()
