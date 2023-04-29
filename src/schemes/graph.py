from uuid import UUID

from .base import BaseSchema


class PointsSchema(BaseSchema):

    graph_id: UUID
    points_X: list[float]
    points_Y: list[float]
