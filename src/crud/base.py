from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from services.preparation import PreparationGraph


class BaseCRUD:
    def __init__(self, model):
        self._model = model

    async def create(self, points, session: AsyncSession):
        obj = jsonable_encoder(points)
        target = PreparationGraph(obj)
        for value in target.prepare():
            item = self._model(**value)
            session.add(item)
        await session.commit()
