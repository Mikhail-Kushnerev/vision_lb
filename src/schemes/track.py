"""Pydantic-схема описывания трека."""

from uuid import UUID

from pydantic import Field, BaseModel

from .base import BaseSchema


class PointSchema(BaseModel):
    """Класс описывает точки по осям Х и У."""

    x: float = Field(
        ...,
        title='Точка X',
        description='Значение точки на оси X'
    )
    y: float = Field(
        ...,
        title='Точка Y',
        description='Значение точки на оси Y'
    )


class BodySchema(BaseSchema):
    """Класс описывает тело-запроса по созданию трека."""

    track_id: UUID = Field(
        ...,
        title='идентификатор трека',
        description='Этот `id` необходим для построения '
    )
    points: list[PointSchema] = Field(
        ...,
        title='Координаты точек',
        description='Значения точек по оси Х и У'
    )
