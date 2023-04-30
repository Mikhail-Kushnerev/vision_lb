from uuid import UUID

from pydantic import Field, BaseModel

from .base import BaseSchema


class Point(BaseModel):
    x: float
    y: float


class Body(BaseSchema):
    graph_id: UUID = Field(
        ...,
        title='идентификатор трэка',
        description='Этот `id` необходим для построения '
    )
    points: list[Point] = Field(
        ...,
        title='Координаты точек',
        description='Значения точек по оси Х и У'
    )
