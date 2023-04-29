from .base import BaseSchema


class PointsSchema(BaseSchema):

    points_x: list[float]
    points_y: list[float]
